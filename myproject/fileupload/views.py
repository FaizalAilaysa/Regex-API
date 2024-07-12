from rest_framework import status
from rest_framework.parsers import MultiPartParser , FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UploadFileSerializer
import re
import os
from docx import Document  

class FileUploadView(APIView):
    """
    API view to handle file uploads, correct mistakes, and return the corrected content.
    """
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request, *args, **kwargs):
        
        """
        Handle POST request for file upload and process the content.

        Request:
            request (HttpRequest): The request object containing the uploaded file.
        Returns:
            Response: A response object containing the corrected content or errors.
        """
        
        file_serializer = UploadFileSerializer(data=request.data)
        
        if file_serializer.is_valid():
            file_instance = file_serializer.save()
            
            file_path = file_instance.file.path
            file_name, file_extension = os.path.splitext(file_path)

            if file_extension == '.docx':
                content = self.read_docx_file(file_path)
            else:
                with open(file_path, 'r') as file:
                    content = file.read()
                
            corrected_content = self.correct_mistakes(content)
            return Response({'corrected_content': corrected_content}, status=status.HTTP_200_OK)
        
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
    
    def read_docx_file(self, file_path):
        """
        Read content from a DOCX file.
        
        file_path (str): The path to the DOCX file.

        Returns:
            str: The content of the DOCX file as a string.
        """
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return ''.join(full_text)
    
    def correct_mistakes(self, content):
        """
        Correct mistakes in the given content using regex patterns.

        content (str): The original content to be corrected.

        Returns:
            str: The corrected content.
        """
        
        corrections = [
            (r'\s*,', r','),  # Remove spaces before commas
            (r'\(\s*(.*?)\s*\)', r'(\1)'),  # Remove spaces inside parentheses
            (r'\s*\?', r'?'),  # Remove spaces before question marks
            (r'\s*:', r':'),  # Remove spaces before colons
            (r'\s*;', r';'),  # Remove spaces before semicolons
            (r'\s*!', r'!'),  # Remove spaces before exclamation marks
            (r'\$\s*(\d+)', r'$\1'),  # Remove spaces after dollar signs
            (r'\s*\'', r'\''),  # Remove spaces before apostrophes
            (r'"\s*(.*?)\s*"', r'"\1"'),  # Remove spaces inside double quotes
            (r'\band\s*/\s*or\b', r'and/or'),  # Remove spaces around slashes in "and / or"
            (r'\\n', r' '),  # Replace \n with space
            (r'\s+', r' '),  # Replace multiple spaces with a single space
            (r'\\"', r'"'),  # Remove backslash before double quotes
            (r"\\'", r"'"),  # Remove backslash before single quotes
        ]
        for pattern, replacement in corrections:
            content = re.sub(pattern, replacement, content)
        return content






