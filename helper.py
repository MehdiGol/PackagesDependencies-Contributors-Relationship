import pathlib
import pandas
import collections

CURRENT_PATH = pathlib.Path(__file__).absolute().parent

DATA_PATH = CURRENT_PATH / 'data'

GIT_API = ['5da1276e73fbfda3c268:35e6eb9e99f74000131e20e4caa644a546dd384d',
           'e96241ca553fb9cf4d1b:979ecb8c98fdcddfa7921623daa4dacb3fa415b4',
           '7d401956aa5c0afcf7f9:0f89c5e4ecd30a36aef65f3b0dcbbd120d534fb0',
           'fe0f71d5267a85bb0345:05d5125ab433595d8e15d3cbb1ad13ae95c1d9c2',
           '76997fa7dd9cf9f4872f:d8754621a63f1d33d5c0427b2efafb94141b8c70',
           '53a9c2f81aeb70d453b9:8bb7576c10cf1340e833acc791a7259786ca11c8',
           '093a7ed958a206f60a37:3dc925411cdea302056f7d22a5123efe2dbad079',
           '9fd9b488461473c436a6:3545408a65ba7929f28a56fbc2475bd3c592379b',
           'a490a4a97ea7b9cab562:a8412ae2115935e1a6313c535f666ff9ecca4c79',
           '57aabf73d33083f3c49f:cf81d09889b6c768eab39e2c8c259bfc8b1c4488',
           '165af6758225e8017e62:cb905bd2ab24e39b10f47a99eec012c65b4a566f',
           '0b2f27dac3c25848eb7f:4f9d27ca9810ce46f7a317c63dde389f287aa4dc',
	   'ea4b6eec52dce28ec7fa:7959c04f36e84e8c701279b3cea1aef8b596088a',
           '13ebff80c1f67316e889:2e9cc995164db8438dd7f776ab53af4592353c1f',
           'be243f299d5b56b105e0:3982847d4312aa7cbed09da43cf6f39ace1beb6a',
           '1b08271f98996e347123:d8e0dfbe1fd136b76585a50d7e89b80492f0fb4e',
           'fe57e2e032d3230c1766:244315313d02e9146061bc6946c61d145121fbbe',
           'c2bf131a500f55730b6c:b9e8de22e6575495eb493b18fcebd48d0df6ffef',
           '2d7a20e9b74893c3aca7:ceeb0fb792c336f8567981881798d906f9948118',
           'dda03c75918b37514d85:8e1760a5500fd75d73452e0a8329d0b1f15c4be2',
           '1ba77e5c592d462e7ae4:535199ceacbda6130156b0ebda64926a6e139c5d',
           'ff9e74acc730af8ead4d:811f5bee820d058aad60d32fed3074d535201f95',
           'ef066c3b2f51f82e904b:11984fde063725cb1c0e982033903d52b789b562',
           'bbb3a7cd0b231237aac5:c9e66b2b92ee97660e2c38254f802e305b8e8ab4']

def clean_data(packages, dependencies, ecosystem=None):
    """
    Remove invalid or unknown packages and dependencies.
    """
    # Filter releases with invalide date
    packages = (
        packages[packages['date'] >= pandas.to_datetime('1980-01-01')]
        .dropna()
    )

    # For npm, remove packages starting with:
    # - all-packages-
    # - cool-
    # - neat-
    # - wowdude-
    # This represents around 245 packages with have a very high number
    # of dependencies, and are just "fun packages", as explained here:
    # https://libraries.io/npm/wowdude-119
    if ecosystem == 'npm':
        filtered = ('all-packages-', 'cool-', 'neat-', 'wowdude-',)
        packages = packages[~packages['package'].str.startswith(filtered)]

    # Filter unknown package/version
    dependencies = dependencies.merge(
        packages[['package', 'version']],
        how='inner'
    )
    
    # Filter unknown dependencies
    d_before = len(dependencies)
    dependencies = dependencies[dependencies['target'].isin(packages['package'])]
    d_after = len(dependencies)
    
    # print('{}: from {} deps to {} deps'.format(
    #     ecosystem,
    #     d_before,
    #     d_after,
    # ))

    return packages, dependencies

def load_data(ecosystem):
    """
    Return a pair (packages, dependencies) of dataframes for the given ecosystem.
    """
    # Load data files
    packages = pandas.read_csv(
        (DATA_PATH / '{}-versions.csv.gz'.format(ecosystem)).as_posix(),
        usecols=['package', 'version', 'date'],
        parse_dates=['date'],
        infer_datetime_format=True,
        engine='c',
    )
    
    dependencies = pandas.read_csv(
        (DATA_PATH / '{}-dependencies.csv.gz'.format(ecosystem)).as_posix(),
        usecols=['package', 'version', 'target', 'constraint'],
        engine='c',
    )
    
    return clean_data(packages, dependencies, ecosystem)

def load_repo(ecosystem):
    """
    Return a pair ecosystem data.
    """
    # Load data files
    repo = pandas.read_csv(
        (DATA_PATH / '{}-repos.csv.gz'.format(ecosystem)).as_posix(),
        engine='c',
    )
    
    return repo

def read_comments():
    depend_comt = pandas.read_csv('../data/depend/commit_comment.csv.gz').dropna().rename(columns={'comment_author_assoc':'author_assoc','user_name':'user_login','comment_created_at':'created_at'})
    depend_comt['type'] = 'cmt'
    depend_isue = pandas.read_csv('../data/depend/issue_comments.csv.gz')
    depend_isue['type'] = 'isu'
    depend_puls = pandas.read_csv('../data/depend/pulls_comments.csv.gz')
    depend_puls['type'] = 'pul'
    depend_plrq = pandas.read_csv('../data/depend/pulls_review_comments.csv.gz')
    depend_plrq['type'] = 'prq'

    origin_comt = pandas.read_csv('../data/origin/commit_comment.csv.gz')
    origin_comt = origin_comt.dropna().rename(columns={'comment_author_assoc':'author_assoc','user_name':'user_login','comment_created_at':'created_at'})
    origin_comt['type'] = 'cmt'
    origin_isue = pandas.read_csv('../data/origin/issue_comments.csv.gz')
    origin_isue['type'] = 'isu'
    origin_puls = pandas.read_csv('../data/origin/pulls_comments.csv.gz')
    origin_puls['type'] = 'pul'
    origin_plrq = pandas.read_csv('../data/origin/pulls_review_comments.csv.gz')
    origin_plrq['type'] = 'prq'
    
    all_comments = depend_comt[['project_name','user_login','author_assoc','created_at','type']].append(
                   depend_isue[['project_name','user_login','author_assoc','created_at','type']]).append(
                   depend_puls[['project_name','user_login','author_assoc','created_at','type']]).append(
                   depend_plrq[['project_name','user_login','author_assoc','created_at','type']]).append(
                   origin_comt[['project_name','user_login','author_assoc','created_at','type']]).append(
                   origin_isue[['project_name','user_login','author_assoc','created_at','type']]).append(
                   origin_puls[['project_name','user_login','author_assoc','created_at','type']]).append(
                   origin_plrq[['project_name','user_login','author_assoc','created_at','type']])
    cargo = load_repo('Cargo')
    cargo_git = cargo[cargo.Repository_URL.notnull()]
    cargo_git = cargo_git[cargo_git.Repository_URL.str.contains('github')].drop_duplicates(subset='Repository_URL')
    repos = cargo_git[['Name','Repository_URL']]
    
    all_comments_repos = all_comments.merge(repos.reset_index(),left_on='project_name', right_on='Repository_URL')[['Name','user_login','author_assoc','created_at','type']]
    
    return all_comments_repos