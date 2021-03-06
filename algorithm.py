import graph_tool.all as gt
import numpy as np 
from itertools import product
def reshape_func(k, choice = 'id'):
	"""
	Vectorized reshaping function.
	"""
	if choice == 'id':
		return k

def BH(p_vals, alpha):
	"""
	Inputs:

	p_vals: an array of p values

	alpha: significance level

	Outputs:

	A boolean array. 
	True indicates rejecting H0.
	"""
	n = len(p_vals)
	sorted_inds = np.argsort(p_vals)

	# Whether rejecting H0 based on sorted p values.
	ifreject = p_vals[sorted_inds] <= reshape_func(np.arange(1,n+1)) * \
	(alpha/float(n))

	reverse_inds = np.zeros(n,dtype=int)
	reverse_inds[sorted_inds] = np.arange(n)

	# Return whether rejecting H0 in the order of original p values.
	return ifreject[reverse_inds]
	
def get_1_neighbours(graph, i):
	"""
	This function gets all the 1-neighborhoods including i itself. 
	"""
	nbhd_nodes = graph.get_out_neighbours(i)
	nbhd_nodes = np.concatenate((nbhd_nodes,np.array([i])))
	return nbhd_nodes

def get_c_neighbours(graph, i, c, upper,right):
	"""
	This function returns all nodes that within distance <=c on a grid graph.

	It requires a grid graph with nodes numbered in order. 

	This function is used in multi-step QuTE. 

	Input:
	graph: a gt.Graph object.

	i: The node whose k-neighbours to be returned.

	c: The distance to be considered

	upper: The height of the grid graph - 1

	right: The width of the grid graph - 1

	Output:

	An array contains the indices of all nodes that within distance <=c.
	"""
	
	x = i % (right + 1)
	y = i // (right + 1)
	nbhd = []
	delta_xids = np.arange(-c,c+1,1)
	delta_yids = np.arange(-c,c+1,1)

	xids = x + delta_xids
	yids = y + delta_yids

	coords = np.array(list(product(xids, yids)))
	coords = np.array([coord for j, coord in enumerate(coords) \
	if abs(coord[0] - x)+abs(coord[1] - y)<=c and \
	coord[0] <= right and \
	coord[1] <= upper and \
	coord[0]>= 0 and coord[1]>= 0]) 
	return np.array([y * (right + 1) + x for x,y in coords]) 

def generalized_BH_original(graph, p_vals, alpha, get_nbhd = get_1_neighbours):
	"""
	Inputs:
	graph: The underlying graph structure. A gt.Graph object.

	alpha: significance level 

	get_nbhd: For generic graph, it is default as get_1_neighbours.
	For grid graphs, it requires a function mapping an index to all of its 
	within-k-distance neighbors, for a k to be chosen.

	Return: 
	A boolean array indicating wehther to reject on each node.
	"""
	num_nodes = graph.num_vertices()

	ifreject = np.array([False] * num_nodes)
  
	for i in xrange(num_nodes):
 
		nbhd_nodes = get_nbhd(graph, i).astype(int)

		# In the nbhd, do a BH test with adjusted alpha.
		local_rejection = BH(p_vals[nbhd_nodes],alpha * \
			len(nbhd_nodes) / float(num_nodes))

		ifreject[nbhd_nodes] = \
		np.logical_or(ifreject[nbhd_nodes],local_rejection) 

	return ifreject

def generalized_BH(data,alpha,get_nbhd = get_1_neighbours):
	"""
	Inputs:

	data: Object generated by make_data.py

	alpha: significance level

	data will be assigned a new attribute, a boolean vector
	indicating whether each node is rejected or not.   

	Return: None
	""" 

	data.ifreject = generalized_BH_original(data.graph, 
		data.p_vals, alpha, get_nbhd = get_nbhd)












