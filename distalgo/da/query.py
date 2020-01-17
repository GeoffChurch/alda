import os
from minizinc import Instance, Model, Solver
MZ_MODEL_HOME = os.path.join(os.path.dirname(__file__),'compiler','constraint','minizinc_model_test')

from pprint import pprint

SOVLER_DEFAULT = 'gecode'

def flat_list(inputlist, dimension=1, current_len=[]):
	if isinstance(inputlist,list) and len(inputlist) > 0 and isinstance(inputlist[0],list):
		output = []
		current_len.append(len(inputlist[0]))
		for l in inputlist:
			output += l
		return flat_list(output, dimension+1, current_len)
	elif isinstance(inputlist,list):
		tmplist = ['_' if (l is None) else str(l) for l in inputlist]
		tmplen = ','.join(['1..%s'%l for l in current_len])
		return 'array%sd(%s,[%s])' % (dimension,tmplen,','.join(tmplist))
	else:
		print("TODO: should't get here")

# def flat_set(node):

		

def query(self, constraint, **args):
	_constraint_object = self['_constraint_object']

	model = Model(os.path.join(MZ_MODEL_HOME, constraint+'.mzn'))
	
	datafile = os.path.join(MZ_MODEL_HOME, constraint+'.dzn')
	file = open(datafile,'w')
	returnval = []

	for key in _constraint_object[constraint]:
		if key not in args:
			val = self[key]
		else:
			val = args[key]

		if isinstance(val, list):
			flatten_val = flat_list(val,current_len=[len(val)])
		else:
			flatten_val = str(val)
		file.write('%s = %s;\n' % (key,flatten_val))


	for key, val in args.items():
		# print(key,val)
		if key == 'return_value':
			returnval = set(val)
			continue
		elif key not in _constraint_object[constraint]:
			print('Warning: variable %s is defined in the model, ignored')

		# elif isinstance(val, list):
		# 	flatten_val = flat_list(val,current_len=[len(val)])
		# # elif isinstance(val, set):
		# # 	flatten_val = flat_list(val)
		# else:
		# 	flatten_val = str(val)
		# file.write('%s = %s;\n' % (key,flatten_val))

	file.close()

	model.add_file(datafile)
	solver = Solver.lookup(SOVLER_DEFAULT)
	instance = Instance(solver, model)
	result = instance.solve()
	# pprint(result._solutions[0].assignments)
	if len(result._solutions) == 0:
		return None
	# pprint(result._solutions[-1])
	# TODO: relate objective in minizinc to the variable decalred in the problem
	rt = {key:val for key,val in result._solutions[-1].assignments.items() if key in returnval}

	if result._solutions[-1].objective:
		havename = False
		obj = result._solutions[-1].objective
		for key in returnval:
			if key not in rt:
				rt[key] = result._solutions[-1].objective
				havename = True
				break
		if not havename:
			rt['objective'] = result._solutions[-1].objective
	# print('rt')
	# pprint (rt)

	return rt
	