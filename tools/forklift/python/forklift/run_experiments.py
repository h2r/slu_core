from g3.evaluator.evaluateParallel import evaluateParallel, generate_evaluation_parser
from g3.evaluator.evaluate_nodes import evaluate_nodes
import numpy as na


def main():
    parser = generate_evaluation_parser()

    parser.add_option("--result-fname-base", dest="result_fname_base")
    (options, args) = parser.parse_args()

    results_file = open('results_{:d}'.format(options.run_id), 'a')
    results_file.write('| Run ID | Corpus | Question Type | # Questions | Metric | Merging | Resolver | Random Seed | Object Accuracy | Num Objects | Event Entropy |h')

    values = {'merging': ['1'],
              'resolver_type': ['oracle'],
              'question_type': ['targeted'],
              'entropy_metric': ['random'],
              'num_questions': range(2, 3),
              'random_seed': range(5)}
    for options.use_merging in values['merging']:
        if options.use_merging == '1':
            resolver_values = values['resolver_type']
        else:
            resolver_values = ['oracle']
        for options.resolver_type in resolver_values:
            for options.num_questions in values['num_questions']:
                if options.num_questions > 0:
                    for options.question_type in values['question_type']:
                        if options.question_type == 'reset':
                            create_table_entry_for_run(options, results_file)
                            options.run_id += 1
                        else:
                            for options.entropy_metric in values['entropy_metric']:
                                if options.entropy_metric=='random':
                                    seed_values = values['random_seed']
                                else:
                                    seed_values = [10]
                                for options.random_seed in seed_values:
                                    create_table_entry_for_run(options, results_file)
                                    options.run_id += 1
                else:
                    create_table_entry_for_run(options, results_file)
                    options.run_id += 1

    results_file.close()


def create_table_entry_for_run(options, out_file=None):
    # Save the settings used
    if any('ambiguous' in name for name in options.corpus_fname):
        corpus_name = 'Ambiguous'
    else:
        corpus_name = 'Real'
    options.result_fname = options.result_fname_base + str(options.run_id) + '/'
    print "Running evaluation with options:"
    print options
    options_string = "\n| {:d} | {:s} | {:s} | {:d} | {:s} | {:s} | {:s} | {:d} | ".format(options.run_id, corpus_name, options.question_type, options.num_questions, options.entropy_metric, options.use_merging, options.resolver_type, options.random_seed)
    if out_file:
        out_file.write(options_string)
        out_file.flush()

    # Actually run the evaluation
    evaluateParallel(options)
    cm, event_entropies = evaluate_nodes(options)

    # Save the results
    result_string = "{:.4g} | {:d} | {:.4g} +- {:.4g} |".format(cm.accuracy, cm.num_results, na.mean(event_entropies), na.std(event_entropies))
    if out_file:
        out_file.write(result_string)
        out_file.flush()


if __name__ == '__main__':
    main()
