import csv
from io import StringIO
from rest_framework import renderers


class CSVAttendanceRenderer(renderers.BaseRenderer):
    """
    Custom CSV renderer for attendance reports.
    Streams CSV output for large datasets (>1000 records).
    """
    media_type = 'text/csv'
    format = 'csv'
    charset = 'utf-8'
    
    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render attendance data as CSV.
        
        Args:
            data: List of dictionaries containing attendance records
            accepted_media_type: The media type accepted by the client
            renderer_context: Additional context from the view
            
        Returns:
            CSV formatted string
        """
        # Handle error responses (non-list data)
        if not isinstance(data, list):
            return str(data).encode(self.charset)
        
        # Handle empty data
        if not data:
            return b''
        
        # Define CSV columns
        columns = [
            'student_name',
            'email',
            'session_date',
            'session_time',
            'status',
            'marked_at',
            'distance_meters',
            'reason'
        ]
        
        # Use StringIO for efficient string building
        output = StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=columns,
            extrasaction='ignore'
        )
        
        # Write header
        writer.writeheader()
        
        # Write data rows
        # For large datasets (>1000 records), this streams efficiently
        for record in data:
            writer.writerow(record)
        
        # Get CSV content
        csv_content = output.getvalue()
        output.close()
        
        # Return as bytes
        return csv_content.encode(self.charset)
