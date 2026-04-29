import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { adminAPI } from '../../services/api';
import Modal from '../shared/Modal';

const CourseManagement = () => {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    instructor_id: '',
    department_id: '',
  });
  const [isCreateCourseModalOpen, setIsCreateCourseModalOpen] = useState(false);
  const [isEnrollmentModalOpen, setIsEnrollmentModalOpen] = useState(false);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courseFormData, setCourseFormData] = useState({
    code: '',
    title: '',
    department_id: '',
    instructor_id: '',
  });
  const [enrollmentFormData, setEnrollmentFormData] = useState({
    student_id: '',
    course_id: '',
  });

  // Fetch courses with pagination and filters
  const { data: coursesData, isLoading, error } = useQuery({
    queryKey: ['courses', page, filters],
    queryFn: () => adminAPI.getCourses({ page, ...filters }),
  });

  // Fetch users for instructor/student selection
  const { data: teachersData } = useQuery({
    queryKey: ['teachers'],
    queryFn: () => adminAPI.getUsers({ role: 'teacher', page_size: 100 }),
  });

  const { data: studentsData } = useQuery({
    queryKey: ['students'],
    queryFn: () => adminAPI.getUsers({ role: 'student', page_size: 100 }),
  });

  // Fetch enrollments for selected course
  const { data: enrollmentsData } = useQuery({
    queryKey: ['enrollments', selectedCourse?.id],
    queryFn: () => adminAPI.getEnrollments({ course_id: selectedCourse?.id }),
    enabled: !!selectedCourse,
  });

  // Create course mutation
  const createCourseMutation = useMutation({
    mutationFn: (data) => adminAPI.createCourse(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['courses']);
      setIsCreateCourseModalOpen(false);
      setCourseFormData({ code: '', title: '', department_id: '', instructor_id: '' });
    },
  });

  // Create enrollment mutation
  const createEnrollmentMutation = useMutation({
    mutationFn: (data) => adminAPI.createEnrollment(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['enrollments', selectedCourse?.id]);
      setEnrollmentFormData({ student_id: '', course_id: selectedCourse?.id || '' });
    },
  });

  // Delete enrollment mutation
  const deleteEnrollmentMutation = useMutation({
    mutationFn: (enrollmentId) => adminAPI.deleteEnrollment(enrollmentId),
    onSuccess: () => {
      queryClient.invalidateQueries(['enrollments', selectedCourse?.id]);
    },
  });

  const handleCreateCourse = (e) => {
    e.preventDefault();
    createCourseMutation.mutate(courseFormData);
  };

  const handleCreateEnrollment = (e) => {
    e.preventDefault();
    createEnrollmentMutation.mutate({
      ...enrollmentFormData,
      course_id: selectedCourse.id,
    });
  };

  const handleManageEnrollments = (course) => {
    setSelectedCourse(course);
    setEnrollmentFormData({ student_id: '', course_id: course.id });
    setIsEnrollmentModalOpen(true);
  };

  const handleDeleteEnrollment = (enrollmentId) => {
    if (window.confirm('Are you sure you want to remove this enrollment?')) {
      deleteEnrollmentMutation.mutate(enrollmentId);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const courses = coursesData?.data?.results || [];
  const totalPages = coursesData?.data?.count ? Math.ceil(coursesData.data.count / 50) : 1;
  const teachers = teachersData?.data?.results || [];
  const students = studentsData?.data?.results || [];
  const enrollments = enrollmentsData?.data?.results || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Course Management</h2>
        <button
          onClick={() => setIsCreateCourseModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Create Course
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Instructor
            </label>
            <select
              value={filters.instructor_id}
              onChange={(e) => handleFilterChange('instructor_id', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Instructors</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.full_name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Department ID
            </label>
            <input
              type="text"
              value={filters.department_id}
              onChange={(e) => handleFilterChange('department_id', e.target.value)}
              placeholder="Filter by department..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </div>

      {/* Courses Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading courses...</div>
        ) : error ? (
          <div className="p-8 text-center text-red-500">
            Error loading courses: {error.message}
          </div>
        ) : courses.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No courses found</div>
        ) : (
          <>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Code
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Title
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Instructor
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {courses.map((course) => (
                  <tr key={course.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">
                        {course.code}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">{course.title}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {course.instructor_name || 'N/A'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <button
                        onClick={() => handleManageEnrollments(course)}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        Manage Enrollments
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200">
                <div className="flex-1 flex justify-between sm:hidden">
                  <button
                    onClick={() => setPage(p => Math.max(1, p - 1))}
                    disabled={page === 1}
                    className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages}
                    className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </div>
                <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                  <div>
                    <p className="text-sm text-gray-700">
                      Page <span className="font-medium">{page}</span> of{' '}
                      <span className="font-medium">{totalPages}</span>
                    </p>
                  </div>
                  <div>
                    <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                      <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        Previous
                      </button>
                      <button
                        onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                      >
                        Next
                      </button>
                    </nav>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Create Course Modal */}
      <Modal
        isOpen={isCreateCourseModalOpen}
        onClose={() => setIsCreateCourseModalOpen(false)}
        title="Create New Course"
      >
        <form onSubmit={handleCreateCourse} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Course Code *
            </label>
            <input
              type="text"
              required
              value={courseFormData.code}
              onChange={(e) => setCourseFormData({ ...courseFormData, code: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Course Title *
            </label>
            <input
              type="text"
              required
              value={courseFormData.title}
              onChange={(e) => setCourseFormData({ ...courseFormData, title: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Department ID
            </label>
            <input
              type="text"
              value={courseFormData.department_id}
              onChange={(e) => setCourseFormData({ ...courseFormData, department_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Instructor *
            </label>
            <select
              required
              value={courseFormData.instructor_id}
              onChange={(e) => setCourseFormData({ ...courseFormData, instructor_id: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select Instructor</option>
              {teachers.map((teacher) => (
                <option key={teacher.id} value={teacher.id}>
                  {teacher.full_name}
                </option>
              ))}
            </select>
          </div>
          {createCourseMutation.isError && (
            <div className="text-red-600 text-sm">
              {createCourseMutation.error?.message || 'Failed to create course'}
            </div>
          )}
          <div className="flex justify-end space-x-2">
            <button
              type="button"
              onClick={() => setIsCreateCourseModalOpen(false)}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={createCourseMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {createCourseMutation.isPending ? 'Creating...' : 'Create Course'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Enrollment Management Modal */}
      <Modal
        isOpen={isEnrollmentModalOpen}
        onClose={() => {
          setIsEnrollmentModalOpen(false);
          setSelectedCourse(null);
        }}
        title={`Manage Enrollments - ${selectedCourse?.code}`}
      >
        <div className="space-y-4">
          {/* Add Student Form */}
          <form onSubmit={handleCreateEnrollment} className="space-y-4 pb-4 border-b">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Add Student
              </label>
              <div className="flex space-x-2">
                <select
                  required
                  value={enrollmentFormData.student_id}
                  onChange={(e) => setEnrollmentFormData({ ...enrollmentFormData, student_id: e.target.value })}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select Student</option>
                  {students.map((student) => (
                    <option key={student.id} value={student.id}>
                      {student.full_name} ({student.email})
                    </option>
                  ))}
                </select>
                <button
                  type="submit"
                  disabled={createEnrollmentMutation.isPending}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                >
                  Add
                </button>
              </div>
            </div>
            {createEnrollmentMutation.isError && (
              <div className="text-red-600 text-sm">
                {createEnrollmentMutation.error?.message || 'Failed to add enrollment'}
              </div>
            )}
          </form>

          {/* Enrolled Students List */}
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Enrolled Students</h4>
            {enrollments.length === 0 ? (
              <p className="text-sm text-gray-500">No students enrolled yet</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {enrollments.map((enrollment) => (
                  <div
                    key={enrollment.id}
                    className="flex justify-between items-center p-2 bg-gray-50 rounded"
                  >
                    <span className="text-sm text-gray-900">
                      {enrollment.student_name || 'Unknown Student'}
                    </span>
                    <button
                      onClick={() => handleDeleteEnrollment(enrollment.id)}
                      className="text-red-600 hover:text-red-900 text-sm"
                    >
                      Remove
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default CourseManagement;
