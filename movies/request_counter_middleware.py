from .models import RequestCounter

class RequestCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Increment the request count
        counter = RequestCounter.objects.first()
        if not counter:
            counter = RequestCounter()
        counter.count += 1
        counter.save()

        response = self.get_response(request)
        return response