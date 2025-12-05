from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..models import FaultDetection
from ..utils import detect_fault_ai
import json

def fault_detection(request):
    """AI fault detection - Available to all users"""
    from django.contrib import messages
    
    if request.method == 'POST':
        if 'image' in request.FILES:
            image = request.FILES['image']
            
            try:
                # Save temporary record
                detection = FaultDetection.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    image=image
                )
                
                # Run AI detection
                result = detect_fault_ai(detection.image.path)
                
                # Check if detection failed
                if result.get('fault_type') == 'Error':
                    messages.error(request, f"Detection error: {result.get('description', 'Unknown error')}")
                    # Still show the result page with error info
                    context = {
                        'detection': detection,
                        'fault_type_display': 'Error',
                        'confidence_percentage': 0.0,
                    }
                    return render(request, 'solar/fault_detection_result.html', context)
                
                # Convert confidence to percentage (0-1 to 0-100)
                confidence_percentage = float(result['confidence_score']) * 100
                
                # Update record
                detection.fault_type = result['fault_type']
                detection.confidence_score = confidence_percentage  # Store as percentage
                detection.description = result['description']
                detection.detection_result = result
                detection.save()
                
                # Add formatted fault type name for display
                fault_type_display = result['fault_type'].replace('-', ' ').title()
                if fault_type_display == 'Physical Damage':
                    fault_type_display = 'Physical Damage'
                elif fault_type_display == 'Snow Covered':
                    fault_type_display = 'Snow Covered'
                
                context = {
                    'detection': detection,
                    'fault_type_display': fault_type_display,
                    'confidence_percentage': round(confidence_percentage, 1),
                }
                
                return render(request, 'solar/fault_detection_result.html', context)
                
            except Exception as e:
                import traceback
                error_trace = traceback.format_exc()
                print(f"Fault detection error: {error_trace}")
                messages.error(request, f"An error occurred during detection: {str(e)}")
                return render(request, 'solar/fault_detection.html', {'error': str(e)})
        else:
            messages.error(request, "Please select an image file.")
            
    return render(request, 'solar/fault_detection.html')

@login_required
def fault_detection_history(request):
    """Fault detection history"""
    detections = FaultDetection.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'solar/fault_detection_history.html', {'detections': detections})

@csrf_exempt
def chatbot(request):
    """AI chatbot endpoint using Hugging Face Mistral model"""
    if request.method == 'POST':
        try:
            import os
            from openai import OpenAI
            
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            # Get API key from environment variables
            api_key = os.getenv('HF_TOKEN', '')
            if not api_key:
                return JsonResponse({'error': 'HF_TOKEN not configured'}, status=500)
            
            # Initialize OpenAI client with Hugging Face endpoint
            client = OpenAI(
                base_url="https://router.huggingface.co/v1",
                api_key=api_key,
            )
            
            # Create system prompt for solar-specific responses
            system_prompt = """You are SunSavvy Assistant, an AI helper for a solar panel estimation and fault detection platform. 
            You help users with:
            - Solar panel installation questions
            - Energy savings calculations
            - Solar panel maintenance and fault detection
            - Understanding solar technology
            - Finding service providers
            
            Keep responses concise, helpful, and focused on solar energy topics."""
            
            # Get completion from Mistral model
            completion = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2:featherless-ai",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=200,
                temperature=0.7,
            )
            
            response_text = completion.choices[0].message.content
            
            return JsonResponse({'response': response_text})
            
        except Exception as e:
            print(f"Chatbot error: {e}")
            # Fallback to simple responses if API fails
            response_text = "I'm here to help with solar questions! Ask me about costs, savings, or fault detection."
            
            if 'cost' in message.lower() or 'price' in message.lower():
                response_text = "Solar installation costs vary, but typically range from $10,000 to $25,000. Use our Estimation tool for a precise quote."
            elif 'savings' in message.lower():
                response_text = "Most homeowners save between $20,000 and $90,000 over the life of their solar panel system."
            elif 'fault' in message.lower() or 'detect' in message.lower():
                response_text = "You can use our Fault Detection tool to analyze images of your solar panels for any issues."
            elif 'install' in message.lower():
                response_text = "Solar panel installation typically takes 1-3 days. Check our Service Providers page to find qualified installers."
            elif 'panel' in message.lower() or 'solar' in message.lower():
                response_text = "Solar panels convert sunlight into electricity. They typically last 25-30 years and require minimal maintenance."
            
            return JsonResponse({'response': response_text})
            
    return JsonResponse({'error': 'Method not allowed'}, status=405)
