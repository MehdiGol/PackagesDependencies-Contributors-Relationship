import pathlib
import pandas
import collections

CURRENT_PATH = pathlib.Path(__file__).absolute().parent

DATA_PATH = CURRENT_PATH / 'data'


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

