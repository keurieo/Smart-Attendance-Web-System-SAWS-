import React, { useState } from 'react';

const DataTable = ({
  columns,
  data,
  pagination = true,
  pageSize = 10,
  onRowAction,
  loading = false,
  emptyMessage = 'No data available',
}) => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });

  // Sorting logic
  const sortedData = React.useMemo(() => {
    if (!sortConfig.key) return data;

    const sorted = [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue === null || aValue === undefined) return 1;
      if (bValue === null || bValue === undefined) return -1;

      if (typeof aValue === 'string') {
        return sortConfig.direction === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue);
      }

      if (sortConfig.direction === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return sorted;
  }, [data, sortConfig]);

  // Pagination logic
  const totalPages = Math.ceil(sortedData.length / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedData = pagination ? sortedData.slice(startIndex, endIndex) : sortedData;

  const handleSort = (key) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const renderSortIcon = (columnKey) => {
    if (sortConfig.key !== columnKey) {
      return <span className="ml-1 text-gray-400">⇅</span>;
    }
    return sortConfig.direction === 'asc' ? (
      <span className="ml-1">↑</span>
    ) : (
      <span className="ml-1">↓</span>
    );
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Empty state
  if (!data || data.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <p className="text-gray-500 text-lg">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="overflow-x-auto shadow-md rounded-lg">
        <table className="min-w-full bg-white">
          <thead className="bg-gray-100 border-b">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider ${
                    column.sortable !== false ? 'cursor-pointer hover:bg-gray-200' : ''
                  }`}
                  onClick={() => column.sortable !== false && handleSort(column.key)}
                >
                  <div className="flex items-center">
                    {column.label}
                    {column.sortable !== false && renderSortIcon(column.key)}
                  </div>
                </th>
              ))}
              {onRowAction && (
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                  Actions
                </th>
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {paginatedData.map((row, rowIndex) => (
              <tr key={rowIndex} className="hover:bg-gray-50">
                {columns.map((column) => (
                  <td key={column.key} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {column.render ? column.render(row[column.key], row) : row[column.key]}
                  </td>
                ))}
                {onRowAction && (
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex space-x-2">
                      {onRowAction.edit && (
                        <button
                          onClick={() => onRowAction.edit(row)}
                          className="text-blue-600 hover:text-blue-800 font-medium"
                        >
                          Edit
                        </button>
                      )}
                      {onRowAction.delete && (
                        <button
                          onClick={() => onRowAction.delete(row)}
                          className="text-red-600 hover:text-red-800 font-medium"
                        >
                          Delete
                        </button>
                      )}
                      {onRowAction.custom &&
                        onRowAction.custom.map((action, idx) => (
                          <button
                            key={idx}
                            onClick={() => action.handler(row)}
                            className={`${action.className || 'text-gray-600 hover:text-gray-800'} font-medium`}
                          >
                            {action.label}
                          </button>
                        ))}
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {pagination && totalPages > 1 && (
        <div className="flex justify-between items-center mt-4 px-4">
          <div className="text-sm text-gray-700">
            Showing {startIndex + 1} to {Math.min(endIndex, sortedData.length)} of {sortedData.length} results
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              Previous
            </button>
            {[...Array(totalPages)].map((_, idx) => {
              const page = idx + 1;
              // Show first, last, current, and adjacent pages
              if (
                page === 1 ||
                page === totalPages ||
                (page >= currentPage - 1 && page <= currentPage + 1)
              ) {
                return (
                  <button
                    key={page}
                    onClick={() => handlePageChange(page)}
                    className={`px-3 py-1 border rounded-md ${
                      currentPage === page
                        ? 'bg-blue-600 text-white'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    {page}
                  </button>
                );
              } else if (page === currentPage - 2 || page === currentPage + 2) {
                return <span key={page} className="px-2">...</span>;
              }
              return null;
            })}
            <button
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1 border rounded-md disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-100"
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default DataTable;
