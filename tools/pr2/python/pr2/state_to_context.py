import pickle_util 
import yaml

state = pickle_util.load("red_block_close_to_blue.pck")

print state


context = state.to_context()

yaml.dump(context.toYaml(), open("red_block_close_to_blue.yaml", "w"))
