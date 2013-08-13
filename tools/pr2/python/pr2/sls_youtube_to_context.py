from esdcs.context import Context
import yaml

class SlsYoutubeToContext:
    def __init__(self, context_fnames):
        self.fname_to_context = {}
        print "fnames", context_fnames
        for context_fname in context_fnames:
            try:
                context = Context.fromYaml(yaml.load(open(context_fname)))
                self.fname_to_context[context_fname] = context
            except:
                print "error on", context_fname
                raise

    def context_for_youtube_id(self, youtube_id):
        result_key = None
        for key in self.fname_to_context.keys():
            if youtube_id in key:
                if result_key != None:
                    raise ValueError("More than one key matches id " + `youtube_id`)
                
                result_key = key
        if result_key == None:
            return None
        return self.fname_to_context[result_key]
