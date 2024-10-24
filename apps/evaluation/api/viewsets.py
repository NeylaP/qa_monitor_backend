from rest_framework import viewsets, status
from rest_framework.response import Response
from mongoengine import Q
from ..models import EvaluationResults
from common.helpers.api_responses import api_response

class EvaluationResultsViewSet(viewsets.ViewSet):

    def get_results(self, request):
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        agent_code = request.data.get('agent_code')

        if not start_date or not end_date or not agent_code:
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)

        evaluations = EvaluationResults.objects.filter(
            Q(date__gte=start_date) & Q(date__lte=end_date) & Q(agent=str(agent_code))
        )

        total_scores = []
        evaluations_data = []

        for evaluation in evaluations:
            total = sum(result['qualification'] for result in evaluation.results)
            total_scores.append(total)

            evaluations_data.append({
                'file_name': evaluation.file_name,
                'results': evaluation.results,
                'date': evaluation.date,
                'agent': evaluation.agent,
                'call_type': evaluation.call_type,
                'total': total,
            })

        average_score = sum(total_scores) / len(total_scores) if total_scores else 0
        response_data = api_response(True, {
            'evaluations': evaluations_data,
            'average_score': average_score,
        }, "Successfully retrieved")
        return Response(response_data, status=status.HTTP_200_OK)
