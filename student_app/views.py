from django.shortcuts import render

# Create your views here.

# Auth API
class Registration(APIView):
    serializer_class = CustomUser_serializer
    
    @swagger_auto_schema(tags=['Auth APIs'], request_body=serializer_class, operation_description="API for Registration", operation_summary="Registration API")
    def post(self, request, *args, **kwargs):
        if 'role' not in request.data or not request.data['role']:
            request.data['role'] = 'QR_user'
            
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)