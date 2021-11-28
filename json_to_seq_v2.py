import argparse
import re
import json
import multiprocessing
import itertools
import tqdm
import joblib
import numpy as np
from datetime import datetime

from pathlib import Path
from sklearn import model_selection as sklearn_model_selection

METHOD_NAME, NUM = 'METHODNAME', 'NUM'

parser = argparse.ArgumentParser()
parser.add_argument('--data_dir', required=True, type=str)
parser.add_argument('--valid_p', type=float, default=0.2)
parser.add_argument('--max_path_length', type=int, default=8)
parser.add_argument('--max_path_width', type=int, default=2)
parser.add_argument('--use_method_name', type=bool, default=True)
parser.add_argument('--use_nums', type=bool, default=True)
parser.add_argument('--output_dir', required=True, type=str)
parser.add_argument('--n_jobs', type=int, default=multiprocessing.cpu_count())
parser.add_argument('--seed', type=int, default=239)


def __collect_asts(json_file):
    asts = []
    with open(json_file, 'r', encoding='utf-8') as f:
        for line in f:
            record = json.loads(line.strip())
            if len(record['files']) >1:
                print('helps')
            ast = record['files'][0]

            asts.append(ast)

    return asts


def __terminals(ast, node_index, args):
    stack, paths = [], []

    def dfs(v):
        stack.append(v)
        v_node = ast['vertices'][v]
        #class 
        if 'Class' in v_node['term']:
            if v == node_index:  # Top-level func def node.
                if args.use_method_name:
                    paths.append((stack.copy(), METHOD_NAME))
        else:
            v_type = v_node['term']

            if v_type in ['Empty', 'MemberAccess', 'Boolean', 'Import', 'RequiredParameter', 'Alias', 'Context', 'Integer', 'TextElement', 'Identifier', 'Class', 'Call', 'Null', 'Assignment', 'QualifiedAliasedImport', 'Comment', 'Negate', 'Statements', 'Decorator', 'Return', 'Function']:
                paths.append((stack.copy(), v_node['term']))
            else:
                pass

        children = return_children_nodes(ast['edges'], v)
        if len(children) > 0:
            for child in children:
                dfs(child)

        stack.pop()

    def return_children_nodes(children, vertex):
        query_idx = vertex + 1
        return [i['target'] - 1 for i in ast['edges'] if i['source'] == query_idx]

    dfs(node_index)

    return paths


def __merge_terminals2_paths(v_path, u_path):
    s, n, m = 0, len(v_path), len(u_path)
    while s < min(n, m) and v_path[s] == u_path[s]:
        s += 1

    prefix = list(reversed(v_path[s:]))
    lca = v_path[s - 1]
    suffix = u_path[s:]

    return prefix, lca, suffix


def __raw_tree_paths(ast, node_index, args):
    tnodes = __terminals(ast, node_index, args)

    tree_paths = []
    for (v_path, v_value), (u_path, u_value) in itertools.combinations(
            iterable=tnodes,
            r=2,
    ):
        prefix, lca, suffix = __merge_terminals2_paths(v_path, u_path)
        if (len(prefix) + 1 + len(suffix) <= args.max_path_length) \
                and (abs(len(prefix) - len(suffix)) <= args.max_path_width):
            path = prefix + [lca] + suffix
            tree_path = v_value, path, u_value
            tree_paths.append(tree_path)

    return tree_paths


def __delim_name(name):
    if name in {METHOD_NAME, NUM}:
        return name

    def camel_case_split(identifier):
        matches = re.finditer(
            '.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)',
            identifier,
        )
        return [m.group(0) for m in matches]

    blocks = []
    for underscore_block in name.split('_'):
        blocks.extend(camel_case_split(underscore_block))

    return '|'.join(block.lower() for block in blocks)


def __collect_sample(ast, fd_index, args):
    root = ast['vertices'][fd_index]
    if root['term'] not in ('Class'):
        raise ValueError('Wrong node type.')

    target = root['term']

    tree_paths = __raw_tree_paths(ast, fd_index, args)
    contexts = []
    for tree_path in tree_paths:
        start, connector, finish = tree_path

        start, finish = __delim_name(start), __delim_name(finish)
        connector = '|'.join(ast['vertices'][v]['term'] for v in connector)

        context = f'{start},{connector},{finish}'
        contexts.append(context)

    if len(contexts) == 0:
        return None

    target = __delim_name(target)
    context = ' '.join(contexts)

    return f'{target} {context}'


def __collect_samples(ast, args):
    samples = []
    
    # Parse the AST if it is a class or a function with no parent node
    targets = set()
    for edge_index, edge in enumerate(ast['edges']):
        targets.add(edge['target'])

    for node_index, node in enumerate(ast['vertices']):
        # if ((node['term'] == 'Class') or 
        #     (node['term'] == 'Function' and node['vertexId'] not in targets)):
        if node['term'] == 'Class':
            sample = __collect_sample(ast, node_index, args)
            if sample is not None:
                samples.append(sample)
            break #break on first sample returned 
    return samples


def __collect_all_and_save(asts, args, output_file, labels):
    parallel = joblib.Parallel(n_jobs=args.n_jobs)
    func = joblib.delayed(__collect_samples)
    samples = parallel(func(ast, args) for ast in tqdm.tqdm(asts))
    samples = list(itertools.chain.from_iterable(samples))

    with open(output_file, 'w') as f:
        for line_index, line in enumerate(zip(samples, labels)):
            f.write(str(int(line[1])) + ' ' + line[0] + ('' if line_index == len(samples) - 1 else '\n'))




def main():
    args = parser.parse_args()
    np.random.seed(args.seed)
    print('start')
    print(datetime.now())
    data_dir = Path(args.data_dir)
    positives = __collect_asts(data_dir / 'parsed_positive.json')
    negatives = __collect_asts(data_dir / 'parsed_negative.json')
    print('blah1')
    #trains=1

    positives_labels = np.ones((len(positives),))
    negative_labels = np.zeros((len(negatives),))

    training_set = positives + negatives
    labels = np.concatenate((positives_labels, negative_labels))
    # train, valid = sklearn_model_selection.train_test_split(
    #     trains,
    #     test_size=args.valid_p,
    # )

    #Train ratio
    #60 train 20 val 20 test
    X_train, X_temp, y_train, y_temp = sklearn_model_selection.train_test_split(
        training_set, labels,
        #test_size=args.valid_p,
        test_size=0.4,
    )

    X_test, X_val, y_test, y_val = sklearn_model_selection.train_test_split(
        X_temp, y_temp,
        #test_size=args.valid_p,
        test_size=0.5,
    )


    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    # for split_name, split in zip(
    #         ('train', 'valid', 'test'),
    #         (train, valid, test),
    # ):
    for split_name, split, labels in zip(
        ('train', 'test', 'valid'),
        (X_train, X_test, X_val),
        (y_train, y_test, y_val)
    ):
        # save labels
        output_labels_file = output_dir / f'{split_name}_label_output_file.npy'
        with open(output_labels_file, 'wb') as f:
            np.save(f, labels)

        # save parsed sequence
        output_file = output_dir / f'{split_name}_output_file.txt'
        __collect_all_and_save(split, args, output_file,labels)
    print(datetime.now())
    print('done')
# def main():
#     args = parser.parse_args()
#     np.random.seed(args.seed)
#     print('blah')
#     data_dir = Path(args.data_dir)
#     trains = __collect_asts(data_dir / 'python100k_train.json')
#     evals = __collect_asts(data_dir / 'python50k_eval.json')
#     print('blah1')

#     print(len(trains))
#     train, valid = sklearn_model_selection.train_test_split(
#         trains,
#         test_size=args.valid_p,
#     )
#     test = evals

#     output_dir = Path(args.output_dir)
#     output_dir.mkdir(exist_ok=True)
#     for split_name, split in zip(
#             ('train', 'valid', 'test'),
#             (train, valid, test),
#     ):
#         output_file = output_dir / f'{split_name}_output_file.txt'
#         __collect_all_and_save(split, args, output_file)


if __name__ == '__main__':
    main()
