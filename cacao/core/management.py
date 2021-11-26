import os
import yaml
import numpy as np

from cacao.models import ConcreteModel, ComponentBuilder, Timeseries

def execute_from_command_line(args):

    if len(args) < 2:
        raise ValueError('The command line utility of Cacao expects at least 2 arguments: <command> <project_name>')
    
    # define some basic constants (base_path, etc)
    project_name = args[2]
    settings = load_settings(project_name)

    if args[1] == 'startproject':
        start_project(settings, project_name)
    elif args[1] == 'run':
        if not os.path.isdir(settings['BASE_PATH']):
            raise ValueError("Folder with name <" + settings['BASE_PATH'] + "> doesn't exist")
        # read config file
        run_config = read_run_config(settings)

        # read model file
        model_config = read_model_config(settings)
        
        # read data file
        data_config = read_data_config(settings)
        
        # read timeseries_import
        timeseries = read_timeseries_import(settings)
        
        # setup the model
        model = setup_model(model_config, data_config, timeseries)

        # run simulation/ optimization
        results = run(model, run_config)
                
        # export simulation/optimization results
        export_results(settings, results)
    

def start_project(settings, project_name):
    
    if os.path.isdir(settings['BASE_PATH']):
        input('Folder with name <' + project_name + '> already exists. Are you sure you want to start a new project in this directory?[Y/n]')

    for config in settings:
        if config != 'BASE_PATH':
            file_name = settings[config].split('/')[-1]
            if not os.path.isfile( settings[config] ):
                print('copy ' + os.path.join('../templates', file_name) + ' to ' + settings[config])

def load_settings(project_name):

    BASE_PATH = os.path.join(os.getcwd(), project_name)

    settings = {
        'BASE_PATH': BASE_PATH,
        'RUN_CONFIG_PATH': os.path.join(BASE_PATH, 'config.yml'),
        'MODEL_CONFIG_PATH': os.path.join(BASE_PATH, 'model.yml'),
        'DATA_CONFIG_PATH': os.path.join(BASE_PATH, 'data.yml'),
        'TIMESERIES_IMPORT_PATH': os.path.join(BASE_PATH, 'timeseries_import.csv')
    }
    
    return settings

def read_run_config(settings):

    if not os.path.isfile(settings['RUN_CONFIG_PATH']):
        raise FileNotFoundError('The config.yml file was not found. The path evaluated was <' + settings['RUN_CONFIG_PATH'] + '>')
    
    with open(settings['RUN_CONFIG_PATH'], 'r') as f:
        run_config = yaml.load(f, Loader=yaml.FullLoader)
    
    return run_config

def read_model_config(settings):

    if not os.path.isfile(settings['MODEL_CONFIG_PATH']):
        raise FileNotFoundError('The model.yml file was not found. The path evaluated was <' + settings['MODEL_CONFIG_PATH'] + '>')
    
    with open(settings['MODEL_CONFIG_PATH'], 'r') as f:
        model_config = yaml.load(f, Loader=yaml.FullLoader)
    
    return model_config

def read_data_config(settings):

    if not os.path.isfile(settings['DATA_CONFIG_PATH']):
        raise FileNotFoundError('The data.yml file was not found. The path evaluated was <' + settings['DATA_CONFIG_PATH'] + '>')
    
    with open(settings['DATA_CONFIG_PATH'], 'r') as f:
        data_config = yaml.load(f, Loader=yaml.FullLoader)
    
    return data_config

def read_timeseries_import(settings):

    if not os.path.isfile(settings['TIMESERIES_IMPORT_PATH']):
        raise FileNotFoundError('The timeseries_import.csv file was not found. The path evaluated was <' + settings['TIMESERIES_IMPORT_PATH'] + '>')
    
    timeseries_raw = np.genfromtxt(settings['TIMESERIES_IMPORT_PATH'], delimiter=',', names=True)
    
    timeseries = dict()
    for var_name in timeseries_raw.dtype.names:
        timeseries[var_name] = Timeseries(timeseries_raw['t'], timeseries_raw[var_name])

    return timeseries

def setup_model(model_config, data_config, timeseries):

    model_components = []
    for component, attributes in model_config['components'].items():
        model_component = ComponentBuilder.build(component, attributes)
        model_components.append( model_component )

    model = ConcreteModel( model_components, data_config, timeseries )
    

    return model

def run(model, run_config):
    
    model.initialize(run_config)
    if run_config['mode'] == 'simulation':
        model.run_until(run_config['end_time'])
    
    results = model.get_outputs()
    return results

def export_results(settings, results):
    #print(np.stack(list(results.values())))
    result_values = np.stack(list(results.values())).T
    #print(result_values)
    fname = os.path.join(settings['BASE_PATH'], 'timeseries_export.csv')
    
    # comments as '' to remove # at beginning of header
    header = ','.join(list(results.keys()))
    np.savetxt(fname, result_values, fmt='%.3e', delimiter=',', header=header ,comments='')