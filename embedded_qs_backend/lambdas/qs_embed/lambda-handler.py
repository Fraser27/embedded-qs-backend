import os
import logging
import json, boto3, os, re
logger = logging.getLogger()

dashboard_id_list = re.sub(' ', '', os.environ['DASHBOARD_ID_LIST']).split(',')
dashboard_region = 'us-east-1'
log_level = 'INFO'
env_name = 'dev'
logger.setLevel(log_level)
quick_sight = boto3.client('quicksight', region_name=dashboard_region)
    

def lambda_handler(event, context):
    logger.info("Get QS Embed URL")
    print(event)
    response = None
    # Get AWS Account Id
    aws_account_id = context.invoked_function_arn.split(':')[4]
    # get embed URL
    #response = get_anonymous_quick_sight_dashboard_url(aws_account_id, dashboard_id_list, dashboard_region)
    #response = get_reader_based_quick_sight_dashboard_url(aws_account_id, dashboard_id_list, dashboard_region)
    rls_tag = None
    dash_id = None
    if 'queryStringParameters' in event and event['queryStringParameters']:
        if 'tagValue' in event["queryStringParameters"]:
            rls_tag = event["queryStringParameters"]['tagValue']
            dash_id = event["queryStringParameters"]['dash_id']
    
    response = get_anonymous_dash_v2(aws_account_id, dashboard_id_list, dashboard_region, rls_tag, dash_id)
    dashboardList = []
    for dash in dashboard_id_list:
        dashboardList.append({'dashboard_name': get_dashboard_name(aws_account_id, dash, dashboard_region),
                              'dashboard_id': dash})
    
    # append dashboardList for reference
    response.update({'dashboardList': dashboardList})

    # Return response from get-dashboard-embed-url call.
    return {'statusCode': '200',
            'headers': {"Access-Control-Allow-Origin": "*",
                        "Content-Type": "text/plain"},
            'body': json.dumps(response)
            }


def get_anonymous_quick_sight_dashboard_url(aws_account_id, dashboard_ids, region):
    # Generate Anonymous Embed url
    response = quick_sight.get_dashboard_embed_url(
        AwsAccountId=aws_account_id,
        Namespace='default',
        DashboardId=dashboard_id_list[0],
        AdditionalDashboardIds=dashboard_id_list,
        IdentityType='ANONYMOUS',
        SessionLifetimeInMinutes=120,
        UndoRedoDisabled=False,
        ResetDisabled=False
    )
    return response
    
# Additional Dashboard Ids aee only allowed in anonymous embedding
def get_reader_based_quick_sight_dashboard_url(aws_account_id, dashboard_ids, region):
    # Create QuickSight client
    response = quick_sight.get_dashboard_embed_url(
        AwsAccountId=aws_account_id,
        Namespace='default',
        DashboardId=dashboard_id_list[0],
        IdentityType='QUICKSIGHT',
        SessionLifetimeInMinutes=120,
        UndoRedoDisabled=False,
        ResetDisabled=False,
        UserArn=f'arn:aws:quicksight:us-east-1:{aws_account_id}:user/default/TeamRole/MasterKey'
    )
    return response

def get_dashboard_name(aws_account_id, dashboard_id, region):
    try:
        response = quick_sight.describe_dashboard(AwsAccountId=aws_account_id, DashboardId=dashboard_id)
        return response['Dashboard']['Name']
    except Exception as ex:
        print(f'Dashboard not found {ex}')
        pass
    return 'NA'

def get_anonymous_dash_v2(aws_account_id, dashboard_ids, region, rls_tag, dash_id):
    dash_arns = []
    for dash in dashboard_ids:
        dash_arns.append(f'arn:aws:quicksight:{region}:{aws_account_id}:dashboard/{dash}')
    response = None
    if rls_tag is not None:
        response = quick_sight.generate_embed_url_for_anonymous_user(
            AwsAccountId=aws_account_id,
            SessionLifetimeInMinutes=120,
            Namespace='default',
            SessionTags=[
                {
                    'Key': 'tag_employee',
                    'Value': rls_tag
                },
            ],
            AuthorizedResourceArns=dash_arns,
            ExperienceConfiguration={
                'Dashboard': {
                    'InitialDashboardId': dash_id
                }
            }
        )
    else:
        response = quick_sight.generate_embed_url_for_anonymous_user(
            AwsAccountId=aws_account_id,
            SessionLifetimeInMinutes=120,
            Namespace='default',
            AuthorizedResourceArns=dash_arns,
            ExperienceConfiguration={
                'Dashboard': {
                    'InitialDashboardId': dashboard_ids[0]
                }
            }
            )
        
        
    
    return response
  