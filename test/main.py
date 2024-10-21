import argparse
import json
import time
import os
import networkx as nx
from cdlib import evaluation, algorithms
import sys
import matplotlib.pyplot as plt
import numpy as np


#  ==== CLUSTERING METHODS
class UnipartiteCommunities:
    @staticmethod
    def detect_unipartite_communities(G_part, set_number, methods=None):
        results = {}

        all_one_mode_algs = {
            "unipartite_AGDL": (algorithms.agdl, {"number_communities": 2, "kc": None}),
            "unipartite_DER": (algorithms.der, {}),
            "unipartite_Girvan-Newman": (algorithms.girvan_newman, {"level": 1}),
            "unipartite_Leiden": (algorithms.leiden, {}),
            "unipartite_Louvain": (algorithms.louvain, {}),
           "unipartite_LSWL": (algorithms.lswl, {}),
            "unipartite_MCODE": (algorithms.mcode, {}),
            "unipartite_Paris": (algorithms.paris, {}),
            "unipartite_RB_POTS": (algorithms.rb_pots, {}),
            "unipartite_Surprise_Communities": (algorithms.surprise_communities, {}),
            "unipartite_Threshold_Clustering": (algorithms.threshold_clustering, {}),
            "unipartite_pycombo":(algorithms.pycombo,{}),
            "unipartite_bayan":(algorithms.bayan,{})
        }

        # If no methods specified, use all
        if not methods:
            methods = list(all_one_mode_algs.keys())

        for name in methods:
            if name in all_one_mode_algs:
                alg, params = all_one_mode_algs[name]
                try:
                    communities = alg(G_part.copy(), **params)
                    results[name] = {
                        "communities": communities,
                    }
                except Exception as e:
                    print(f"Failed in " + name)
                    results[f"{name};{set_number};weighted"] = {"error": str(e)}
                    
            elif name.startswith("unipartite_"):
                print(f"Warning: Unknown unipartite method '{name}'. Skipping.")

        return results


class BipartiteCommunities:
    @staticmethod
    def project_graphs_weighted(G):
        nodes_0 = {n for n, d in G.nodes(data=True) if d['bipartite'] == 0}
        nodes_1 = set(G.nodes()) - nodes_0

        p0 = nx.bipartite.overlap_weighted_projected_graph(G, nodes_0)
        p1 = nx.bipartite.overlap_weighted_projected_graph(G, nodes_1)

        return p0, p1

    @staticmethod
    def detect_bipartite_communities(G, methods=None):
        results = {}

        all_bipartite_algs = {
            "bipartite_BiMLPA": (algorithms.bimlpa, {}),
            "bipartite_CONDOR": (algorithms.condor, {}),
            "bipartite_SPECTRAL": (algorithms.spectral, {'kmax':4})
        }

        # If no methods specified, use all
        if not methods:
            methods = list(all_bipartite_algs.keys())

        for name in methods:
            if name in all_bipartite_algs:
                alg, params = all_bipartite_algs[name]
                try:
                    communities = alg(G, **params)
                    results[name] = {
                        "communities": communities,
                    }
                except Exception as e:
                    results[name] = {"error": str(e)}
            elif name.startswith("bipartite_"):
                print(f"Warning: Unknown bipartite method '{name}'. Skipping.")

        return results


#  ==== HELPER METHODS
def get_nodes_by_bipartite_attr(G, value):
    return [node for node, attr in G.nodes(data=True) if attr.get('bipartite') == value]


def create_bipartite_graph_from_file(filename):
    G = nx.Graph()
    G.graph['is_directed'] = False
    try:
        with open(filename, 'r') as f:
            # Read methods from the first line
            methods = f.readline().strip().split()

            # Read Group 1 nodes
            group1 = set(map(int, f.readline().strip().split()))

            # Read Group 2 nodes
            group2 = set(map(int, f.readline().strip().split()))

            # Add nodes to the graph with bipartite attribute set directly
            G.add_nodes_from(group1, bipartite=0)
            G.add_nodes_from(group2, bipartite=1)

            # Read and add edges
            for line in f:
                node1, node2 = map(int, line.strip().split())
                G.add_edge(node1, node2)

        # Verify that the graph is indeed bipartite
        if not nx.is_bipartite(G):
            raise ValueError("The resulting graph is not bipartite.")
        if not nx.bipartite.is_bipartite_node_set(G, get_nodes_by_bipartite_attr(G, 0)):
            raise ValueError("The resulting graph is not bipartite.")

        return G, methods

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

    return None, None  # Return None for both G and methods if any error occurred



def json_serialize(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    else:
        return obj


def calculate_metrics(G, communities):
    metrics = {
       # 'modularity': evaluation.newman_girvan_modularity(G, communities).score,
        #'surprise': evaluation.surprise(G, communities).score,
     #   'significance': evaluation.significance(G, communities).score,
        'average_internal_degree': evaluation.average_internal_degree(G,communities).score,
        'internal_edge_density': evaluation.internal_edge_density(G,communities).score,
        'scaled_density': evaluation.scaled_density(G,communities).score,
        'hub_dominance':evaluation.hub_dominance(G,communities).score,
        'conductance': evaluation.conductance(G,communities).score,
        'amount': communities.__sizeof__()
    }
    return metrics


def split_bipartite_communities(G, communities):
    set0_communities = []
    set1_communities = []
    for community in communities:
        set0_comm = [node for node in community if G.nodes[node]['bipartite'] == 0]
        set1_comm = [node for node in community if G.nodes[node]['bipartite'] == 1]

        if set0_comm and set1_comm:
            sys.exit(1)
        elif set0_comm:
            set0_communities.append(set0_comm)
        elif set1_comm:
            set1_communities.append(set1_comm)

    return set0_communities, set1_communities


def validate_bipartite_clustering(G, communities):
    if not nx.is_bipartite(G):
        return False

    for community in communities:
        bipartite_values = set(G.nodes[node]['bipartite'] for node in community)
        if len(bipartite_values) > 1:
            return False
    return True


def validate_unipartite_clustering(G, communities):
    for community in communities:
        unipartite_values = set(G.nodes[node]['bipartite'] for node in community)
        if len(unipartite_values) > 1:
            print(community)
            return False
    return True


def handle_bipartite(G, set0_results, set1_results, bipartite_results):
    for method in bipartite_results:
        if 'communities' in bipartite_results[method]:
            clustering_result = bipartite_results[method]['communities']

            # Remove empty communities
            clustering_result.communities = [comm for comm in clustering_result.communities if comm]

            # Validate the clustering
            if not validate_bipartite_clustering(G, clustering_result.communities):
                error_message = f"Error: Invalid bipartite clustering for method {method}. Mixed nodes from different partitions."
                print(error_message)
                continue

            # Split communities based on the partition
            set0_communities, set1_communities = split_bipartite_communities(G, clustering_result.communities)

            # Calculate metrics using the original community object
            metrics = calculate_metrics(G, clustering_result)

            # Add to consolidated results
            set0_results[f"{method}"] = {
                "communities": set0_communities,
                "metrics": metrics
            }
            set1_results[f"{method}"] = {
                "communities": set1_communities,
                "metrics": metrics
            }


def handle_unipartite(G_projected, set_results, unipartite_results):
    for method, result in unipartite_results.items():
        if 'communities' in result:
            clustering_result = result['communities']

            if not validate_unipartite_clustering(G_projected, clustering_result.communities):
                error_message = f"Error: Invalid clustering for method {method}. Mixed nodes from different partitions."
                print(error_message)
                continue

            # Remove empty communities
            clustering_result.communities = [comm for comm in clustering_result.communities if comm]

            metrics = calculate_metrics(G_projected, clustering_result)
            set_results[f"{method}"] = {
                "communities": [list(comm) for comm in clustering_result.communities],
                "metrics": metrics
            }


def save_results(G, results, filename):
    serializable_results = {}
    for method, data in results.items():
        serializable_results[method] = {
            "communities": [[int(node) for node in comm] for comm in data["communities"]],
            "metrics": {k: float(v) if isinstance(v, np.number) else v for k, v in data["metrics"].items()}
        }

    with open(filename, 'w') as f:
        json.dump(serializable_results, f, indent=2, default=json_serialize)
    print(f"Results saved to: {filename}")

def print_graph(G, filename):
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                           node_color=['lightblue' if G.nodes[n].get('bipartite') == 0 else 'lightgreen' for n in G.nodes()],
                           node_size=500)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, alpha=0.5)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos)
    
    # Create legend
    lightblue_patch = plt.Line2D([0], [0], marker='o', color='w', label='Set 0 (Constraints)',
                                 markerfacecolor='lightblue', markersize=15)
    lightgreen_patch = plt.Line2D([0], [0], marker='o', color='w', label='Set 1 (Domains)',
                                  markerfacecolor='lightgreen', markersize=15)
    plt.legend(handles=[lightblue_patch, lightgreen_patch], loc='upper right')
    
    plt.title("Graph Visualization")
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(f"{filename}", dpi=300, bbox_inches='tight')
    plt.close()

def save_graph_data(G):
    metrics = {
        "graph_level": {},
        "set0": {},
        "set1": {}
    }

    # Graph-level metrics
    metrics["graph_level"] = {
        "num_nodes": G.number_of_nodes(),
        "num_edges": G.number_of_edges(),
       # "is_connected": nx.is_connected(G),
     #   "average_clustering": nx.average_clustering(G),
        "density": nx.density(G),
     #   "average_shortest_path_length": nx.average_shortest_path_length(G) if nx.is_connected(G) else "N/A (Graph is not connected)",
        #"diameter": nx.diameter(G) if nx.is_connected(G) else "N/A (Graph is not connected)",
        "degree_assortativity": nx.degree_assortativity_coefficient(G),
        "average_degree": sum(dict(G.degree()).values()) / G.number_of_nodes(),
    }

    # Bipartite-specific metrics
    nodes_0 = set(n for n, d in G.nodes(data=True) if d['bipartite'] == 0)
    nodes_1 = set(G.nodes()) - nodes_0

    metrics["graph_level"]["set0_size"] = len(nodes_0)
    metrics["graph_level"]["set1_size"] = len(nodes_1)
    metrics["graph_level"]["set0_density"] = nx.bipartite.density(G, nodes_0)
    metrics["graph_level"]["robins_alexander_clustering"] = nx.bipartite.robins_alexander_clustering(G)

    # Set-specific metrics
    eigenvector_centrality = nx.eigenvector_centrality_numpy(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)
    pagerank = nx.pagerank(G)

    def get_degree(node):
        return G.degree(node) if isinstance(G.degree(node), int) else G.degree(node)[1]

    for node in nodes_0:
        metrics["set0"][str(node)] = {
            "degree": get_degree(node),
            "eigenvector_centrality": eigenvector_centrality[node],
            "betweenness_centrality": betweenness_centrality[node],
            "closeness_centrality": closeness_centrality[node],
            "pagerank": pagerank[node],
            "clustering_coefficient": nx.clustering(G, node)
        }

    for node in nodes_1:
        metrics["set1"][str(node)] = {
            "degree": get_degree(node),
            "eigenvector_centrality": eigenvector_centrality[node],
            "betweenness_centrality": betweenness_centrality[node],
            "information_centrality": betweenness_centrality[node],
            "closeness_centrality": closeness_centrality[node],
            "pagerank": pagerank[node],
            "clustering_coefficient": nx.clustering(G, node)
        }

    metrics["graph_level"]["avg_degree_set0"] = sum(get_degree(node) for node in nodes_0) / len(nodes_0)
    metrics["graph_level"]["avg_degree_set1"] = sum(get_degree(node) for node in nodes_1) / len(nodes_1)

    # Additional set-level metrics
    metrics["graph_level"]["avg_eigenvector_centrality_set0"] = sum(eigenvector_centrality[n] for n in nodes_0) / len(nodes_0)
    metrics["graph_level"]["avg_eigenvector_centrality_set1"] = sum(eigenvector_centrality[n] for n in nodes_1) / len(nodes_1)
    metrics["graph_level"]["avg_betweenness_centrality_set0"] = sum(betweenness_centrality[n] for n in nodes_0) / len(nodes_0)
    metrics["graph_level"]["avg_betweenness_centrality_set1"] = sum(betweenness_centrality[n] for n in nodes_1) / len(nodes_1)
    metrics["graph_level"]["avg_closeness_centrality_set0"] = sum(closeness_centrality[n] for n in nodes_0) / len(nodes_0)
    metrics["graph_level"]["avg_closeness_centrality_set1"] = sum(closeness_centrality[n] for n in nodes_1) / len(nodes_1)
    metrics["graph_level"]["avg_pagerank_set0"] = sum(pagerank[n] for n in nodes_0) / len(nodes_0)
    metrics["graph_level"]["avg_pagerank_set1"] = sum(pagerank[n] for n in nodes_1) / len(nodes_1)

    # Save metrics to a JSON file
    with open("graph_metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2,
                  default=lambda x: str(x) if isinstance(x, (set, np.integer, np.floating)) else x)
    print("Graph metrics saved to: graph_metrics.json")

def get_graph_data(filename):
        # Create bipartite graph and get the method
    G, method = create_bipartite_graph_from_file(filename)
    if G is None:
        return

    save_graph_data(G)

def do_clustering(filename):
    # Create bipartite graph and get the methods
    G, methods = create_bipartite_graph_from_file(filename)
    if G is None:
        return
        
    print_graph(G, f"{filename}_visualization.png")

    # Create projection
    G_projected_0, G_projected_1 = BipartiteCommunities.project_graphs_weighted(G)

    start_time = time.time()
    print("start")
    # Apply the methods on the bipartite graph
    bipartite_methods = [m for m in methods if m.startswith('bipartite_')]
    bipartite_results = BipartiteCommunities.detect_bipartite_communities(G.copy(), bipartite_methods)

    # Apply the methods on the projected graphs
    unipartite_methods = [m for m in methods if m.startswith('unipartite_')]
    unipartite_results_0 = UnipartiteCommunities.detect_unipartite_communities(G_projected_0.copy(), 0, unipartite_methods)
    unipartite_results_1 = UnipartiteCommunities.detect_unipartite_communities(G_projected_1.copy(), 1, unipartite_methods)
    end_time = time.time()

    # Calculate and print the time difference
    execution_time = end_time - start_time
    print(f"Total execution time: {execution_time:.4f} seconds")

    base_filename = os.path.splitext(filename)[0]

    # = OUTPUT
    set0_results = {}
    set1_results = {}

    # Process bipartite results
    handle_bipartite(G, set0_results, set1_results, bipartite_results)

    # Process unipartite results
    handle_unipartite(G_projected_0, set0_results, unipartite_results_0)
    handle_unipartite(G_projected_1, set1_results, unipartite_results_1)

    # Save consolidated results
    save_results(G_projected_0, set0_results, f"{base_filename}_set0_results.json")
    save_results(G_projected_1, set1_results, f"{base_filename}_set1_results.json")

def main():
    filename = 'INPUT.txt'
    while True:
        # Wait for input to wake up
        command = input("Press Enter to re-run")
        print()  # This ensures a newline after user input

        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found.")
            continue


        try:
            if command == 'cluster':
                do_clustering(filename)
                print(f"Finished processing {filename}")
            elif command == 'info':
                get_graph_data(filename)
                print(f"Finished processing {filename}")
            elif command == 'dummy':
            	print(f"Finished processing")
            else:
                raise Exception('Error: wrong name')
        except ValueError as ve:
            print(f"Error: {str(ve)}")
            
        except Exception as e:
            print(f"Error: occurred while processing {filename}: {str(e)}")
            
			
        print("\nWaiting for next run...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting the program.")
        sys.exit(0)
