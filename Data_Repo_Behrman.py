import unittest
import os
from prettytable import PrettyTable

class Student:
    def __init__(self, cwid, name, major):
        """create instance of Student class"""
        self.cwid = cwid
        self.name = name
        self.major = major
        self.grades = {} # grades[course] = grade
        self.completed = [] # completed courses (grades above 'C')
        self.req = [] # remaining required courses in major (not taken or grade below 'C')
        self.elec = [] # all available electives unless one alreday taken and passed
    
class Instructor:
    def __init__(self, cwid, name, dept):
        """create instance of Instructor class"""
        self.cwid = cwid
        self.name = name
        self.dept = dept
        self.courses = {} # courses[course] = total enrollment

class Major:
    def __init__(self, dept):
        """create instance of Major class"""
        self.dept = dept
        self.required = []
        self.electives = []

class Repository:
    def __init__(self, dir_path):
        """create instance of Repository class"""
        self.students = {} # students[cwid] = Student
        self.instructors = {} # instructor[cwid] = Instructor
        self.majors = {} # majors[major] = Major
        self.dir_path = dir_path

    def scan(self, dir):
        """Scan a directory for specific '.txt' files and add to student and instructor containers in repository"""
        try:
            os.chdir(dir)
        except ValueError:
            print("Can't open", dir)
        else:
            for student_cwid, name, major in self.add_people("students.txt", 3):
                self.students[student_cwid] = Student(student_cwid, name, major)
            for instructor_cwid, name, dept in self.add_people("instructors.txt", 3):
                self.instructors[instructor_cwid] = Instructor(instructor_cwid, name, dept)
            self.add_major("majors.txt", self.majors)
            self.add_grades("grades.txt", self.students, self.instructors)
            self.major_progress(self.students, self.majors)
        
            major_pt = PrettyTable(field_names=['Dept', 'Required', 'Electives'])
            for major in self.majors:
                major_pt.add_row([major, sorted(self.majors[major].required), sorted(self.majors[major].electives)])
            print(major_pt)

            student_pt = PrettyTable(field_names=['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Requied', 'Remaining Electives'])
            for cwid in self.students: 
                student_pt.add_row([cwid, self.students[cwid].name, self.students[cwid].major, sorted(self.students[cwid].completed), 
                                    sorted(self.students[cwid].req), sorted(self.students[cwid].elec)]) 
            print(student_pt)

            instructor_pt = PrettyTable(field_names=['CWID', 'Name', 'Dept', 'Course', 'Students'])
            for cwid in self.instructors: 
                for course in self.instructors[cwid].courses: 
                    instructor_pt.add_row([cwid, self.instructors[cwid].name, self.instructors[cwid].dept, course, self.instructors[cwid].courses[course]])
            print(instructor_pt)    

    def add_people(self, file, num_fields):
        """for each line in path, yield the fields (to be added to the Students or Instructors dictionary)"""
        try:
            fp = open(file, 'r')
        except ValueError:
            print("Can't open", file)
        else:
            with fp: 
                for n, line in enumerate(fp): 
                    fields = line.strip().split('\t')
                    if len(fields) != num_fields: 
                        raise ValueError("'{}' line: {}: read {} fields but expected {}".format(file, n + 1, len(fields), num_fields)) 
                    else: 
                        yield fields 

    def add_grades(self, file, students, instructors):
        """add grades to students in student container and courses and enrollment totals to instructor container"""
        try:
            fp = open(file, 'r')
        except ValueError:
            print("Can't open", file)
        else:
            with fp:
                for line in fp:
                    student_cwid, course, grade, instructor_cwid = line.strip().split('\t')
                    if student_cwid in students: 
                        students[student_cwid].grades[course] = grade 
                    else:
                        print("No student found matching CWID {}".format(student_cwid))
                    if instructor_cwid in instructors:
                        if course in instructors[instructor_cwid].courses:
                            instructors[instructor_cwid].courses[course] += 1
                        else:
                            instructors[instructor_cwid].courses[course] = 1
                    else:
                        print("No instructor found matching CWID {}".format(instructor_cwid))
    
    def add_major(self, file, majors):
        """iterate through courses in file and sort into Majors"""
        try:
            fp = open(file, 'r')
        except ValueError:
            print("Can't open", file)
        else:
            with fp: 
                for n, line in enumerate(fp): 
                    major, flag, course = line.strip().split('\t')
                    if major in self.majors:
                        if flag == 'R':
                            self.majors[major].required.append(course)
                        elif flag == 'E':
                            self.majors[major].electives.append(course)
                        else:
                            print("{} is not a required or elective course in {}".format(course, major))
                    else:
                        if flag == 'R':
                            self.majors[major] = Major(major)
                            self.majors[major].required.append(course)
                        elif flag == 'E':
                            self.majors[major] = Major(major)
                            self.majors[major].electives.append(course)
                        else:
                            print("{} is not a required or elective course in {}".format(course, major))

    def major_progress(self, students, majors):
        """iterate through student courses for requirement and elective completion"""
        passing = ['A', 'A-', 'B+', 'B', 'B-', 'C+', 'C']
        for student in students:
            maj = students[student].major
            if maj in majors:
                for req in majors[maj].required:
                    students[student].req.append(req)
                for req in majors[maj].electives:
                    students[student].elec.append(req)                
                for course in students[student].grades:
                    if students[student].grades[course] in passing:
                        students[student].completed.append(course)
                        if course in majors[maj].required:
                            students[student].req.remove(course)
                        if course in majors[maj].electives:
                            students[student].elec.remove(course)
            if len(students[student].elec) != len(majors[maj].electives):
                students[student].elec = ['None']

class HomeworkTests(unittest.TestCase):
    def test_student_init(self):
        """test Student __init__(self, cwid, name, major)"""
        s = Student('12345', 'John Doe', 'Science')
        self.assertEqual(s.cwid, '12345')
        self.assertEqual(s.major, 'Science')
        self.assertEqual(s.name, 'John Doe')

    def test_instructor_init(self):
        """test Instructor __init__(self, cwid, name, dept)"""
        i = Instructor('23456', 'Jane Doe', 'Engineering')
        self.assertEqual(i.cwid, '23456')
        self.assertEqual(i.dept, 'Engineering')
        self.assertEqual(i.name, 'Jane Doe')
    
    def test_major_init(self):
        """test Major __init___(self, dept)"""
        m = Major('CSS')
        self.assertEqual(m.dept, 'CSS')

    def test_repository_init(self):
        """test Repository __init__(self, dir_path)"""
        r = Repository('/here/is/a/path')
        self.assertEqual(r.dir_path, '/here/is/a/path')

    def test_add_people_students(self):
        """test add_people(self, path) for students"""
        test_repo = Repository("/Users/ALEX/Documents/Stevens/SSW810/Homework/HW9/testfiles")
        for student_cwid, name, major in  test_repo.add_people("students.txt", 3):
            test_repo.students[student_cwid] = Student(student_cwid, name, major)
        self.assertEqual(test_repo.students['10103'].cwid, '10103')
        self.assertEqual(test_repo.students['10172'].name, 'Forbes, I')
        self.assertEqual(test_repo.students['10183'].major, 'SFEN')

    def test_add_peeople_instructors(self):
        """test add_people(self, path) for instructors"""
        test_repo = Repository("/Users/ALEX/Documents/Stevens/SSW810/Homework/HW9/testfiles")
        for instructor_cwid, name, dept in test_repo.add_people("instructors.txt", 3):
            test_repo.instructors[instructor_cwid] = Instructor(instructor_cwid, name, dept)
        self.assertEqual(test_repo.instructors['98765'].cwid, '98765')
        self.assertEqual(test_repo.instructors['98762'].name, 'Hawking, S')
        self.assertEqual(test_repo.instructors['98760'].dept, 'SYEN')

    def test_add_grades(self):
        """test add_grades(self, file, students, instructors)"""
        test_repo = Repository("/Users/ALEX/Documents/Stevens/SSW810/Homework/HW9/testfiles")
        for student_cwid, name, major in  test_repo.add_people("students.txt", 3):
            test_repo.students[student_cwid] = Student(student_cwid, name, major)
        for instructor_cwid, name, dept in test_repo.add_people("instructors.txt", 3):
            test_repo.instructors[instructor_cwid] = Instructor(instructor_cwid, name, dept)
        test_repo.add_grades("grades.txt", test_repo.students, test_repo.instructors)
        self.assertEqual(test_repo.students['11399'].grades, {'SSW 540': 'B'})
        self.assertEqual(test_repo.students['10172'].grades, {'SSW 555': 'A', 'SSW 567': 'A-'})
        self.assertEqual(test_repo.instructors['98765'].courses, {'SSW 567': 4, 'SSW 540': 3})
        self.assertEqual(test_repo.instructors['98762'].courses, {})
    
    def test_add_major(self):
        test_repo = Repository("/Users/ALEX/Documents/Stevens/SSW810/Homework/HW10/testfiles")
        test_repo.add_major("majors.txt", test_repo.majors)
        self.assertEqual(sorted(test_repo.majors['SFEN'].required), ['SSW 540', 'SSW 555', 'SSW 564', 'SSW 567'])
        self.assertEqual(sorted(test_repo.majors['SFEN'].electives), ['CS 501', 'CS 513', 'CS 545'])
        self.assertEqual(sorted(test_repo.majors['SYEN'].required), ['SYS 612', 'SYS 671', 'SYS 800'])
        self.assertEqual(sorted(test_repo.majors['SYEN'].electives), ['SSW 540', 'SSW 565', 'SSW 810'])        
    
    def test_major_progress(self):
        test_repo = Repository("/Users/ALEX/Documents/Stevens/SSW810/Homework/HW10/testfiles")
        for student_cwid, name, major in  test_repo.add_people("students.txt", 3):
            test_repo.students[student_cwid] = Student(student_cwid, name, major)
        for instructor_cwid, name, dept in test_repo.add_people("instructors.txt", 3):
            test_repo.instructors[instructor_cwid] = Instructor(instructor_cwid, name, dept)
        test_repo.add_grades("grades.txt", test_repo.students, test_repo.instructors)
        test_repo.add_major("majors.txt", test_repo.majors)
        test_repo.major_progress(test_repo.students, test_repo.majors)
        self.assertEqual(sorted(test_repo.students['11658'].completed), [])
        self.assertEqual(sorted(test_repo.students['10103'].req), ['SSW 540', 'SSW 555'])
        self.assertEqual(sorted(test_repo.students['11461'].elec), ['SSW 540', 'SSW 565', 'SSW 810'])
        self.assertEqual(sorted(test_repo.students['11788'].elec), ['None'])

def main():
    stevens = Repository("/Users/ALEX/Documents/Stevens/SSW810/Homework/HW10/testfiles")
    stevens.scan(stevens.dir_path)

if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)
    main()