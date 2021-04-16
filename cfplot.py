#!/usr/bin/env python
import boto3
import plotly.graph_objects as go
import fire

def format_time_from_seconds(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours:02}:{minutes:02}:{seconds:02}'

def main(stackname, profile='default', region='us-east-2'):
    session = boto3.session.Session(
        profile_name=profile, region_name=region)
    cloudformation_client = session.client('cloudformation')
    response = cloudformation_client.describe_stack_events(
        StackName=stackname)
    first = True
    start = None
    data = {}
    # Reverse the order to get events oldest to newest
    response['StackEvents'].reverse()
    for r in response['StackEvents']:
        if first:
            start = r['Timestamp']
            first = False
        # Initialize the waterfall for this Resource
        if r['LogicalResourceId'] not in data:
            base = r['Timestamp'] - start
            data[r['LogicalResourceId']] = {
                'result': {
                    'x': [],
                    'y': [],
                    'text': [],
                    'textfont': {"family": "Open Sans, light",
                                 "color": "black"
                                 },
                    'textposition': "outside",
                    'width': 0.5,
                    'base': base.seconds,
                    'measure': [],
                    'increasing': {"marker": {"color": "Teal"}}},
                'start_time': r['Timestamp']}
        # Calculate the distance from stack start
        duration = r['Timestamp'] - data[r['LogicalResourceId']]['start_time']
        # If there are no values recorded for this resource ID, set the first
        # one as an absolute. TODO: this may need to change.
        if len(data[r['LogicalResourceId']]['result']['measure']) == 0:
            data[r['LogicalResourceId']
                 ]['result']['measure'].append('absolute')
        # Otherwise set it as relative
        else:
            data[r['LogicalResourceId']
                 ]['result']['measure'].append('relative')
        # Record the results
        data[r['LogicalResourceId']]['result']['x'].append(
            duration.seconds)
        data[r['LogicalResourceId']]['result']['y'].append(
            r['LogicalResourceId'])
        
        # If this is the last event then set a text label for the
        # total time the resource took to deploy.
        if r['ResourceStatus'] == 'CREATE_COMPLETE':
            resource_duration = sum(data[r['LogicalResourceId']]['result']['x'])
            data[r['LogicalResourceId']]['result']['text'].append(
                format_time_from_seconds(resource_duration))
        else:
            data[r['LogicalResourceId']]['result']['text'].append(
                '')

    total_time = format_time_from_seconds(data[stackname]["result"]["x"][-1])
    
    fig = go.Figure()
    fig.update_layout(title={
        'text': f'<span style="color:#000000">CloudFormation Waterfall - {stackname}<br /><b>Total Time: {total_time}</b></span>'
    },
        showlegend=False,
        height=(len(data)*30),
        font={
        'family': 'Open Sans, light',
        'color': 'black',
        'size': 14
    },
        plot_bgcolor='rgba(0,0,0,0)')
    fig.update_xaxes(
        tickangle=-45, tickfont=dict(family='Open Sans, light', color='black', size=12))
    fig.update_yaxes(tickangle=0, tickfont=dict(
        family='Open Sans, light', color='black', size=12))
    for k, v in data.items():
        fig.add_trace(go.Waterfall(orientation='h', **v['result']))
    fig.show()


if __name__ == '__main__':
    fire.Fire(main)
