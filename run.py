import urllib.request
from datetime import date

import pandas as pd
import plotly.express as px
import podcastparser
import ruamel.yaml


def parse(feed):
    parsed = podcastparser.parse(feed, urllib.request.urlopen(feed))
    episodes = parsed['episodes']
    return sorted(episodes, key=lambda x: x['published'])


def get_date_and_duration(name, episodes) -> pd.DataFrame:
    dic = {'date': [], 'duration': [], 'name': [], 'one': []}
    for e in episodes:
        dic['date'].append(date.fromtimestamp(e['published']))
        dic['duration'].append(e['total_time']/60/60/24)
        dic['one'].append(1)
        dic['name'].append(name)
    df = pd.DataFrame.from_dict(dic)
    return df


def create_cdf(df):
    fig_dur = px.ecdf(df, x='date', y='duration', color='name',
                      ecdfnorm=None, labels={'duration': 'episode duration (days)'})
    fig_ep = px.ecdf(df, x='date', y='one', color='name',
                     ecdfnorm=None, labels={'one': 'number of episodes'})
    fig_dur.write_image('out/fig_dur.png')
    fig_ep.write_image('out/fig_ep.png')
    fig_dur.write_html('docs/duration.html')
    fig_ep.write_html('docs/number-of-episodes.html')
    # fig_dur.show()
    # fig_ep.show()


def main():
    yaml = ruamel.yaml.YAML()
    with open('shows.yml') as f:
        conf = yaml.load(f)
    print(conf)
    df = None
    for c in conf:
        print(c['name'], c['feed'])
        if c['feed']:
            episodes = parse(c['feed'])
            if df is None:
                df = get_date_and_duration(c['name'], episodes)
            else:
                df = pd.concat(
                    [df, get_date_and_duration(c['name'], episodes)])
    create_cdf(df)


if __name__ == '__main__':
    main()
