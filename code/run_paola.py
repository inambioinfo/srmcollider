#!/usr/bin/python
# -*- coding: utf-8  -*-
# vim:set fdm=marker:
import MySQLdb
import time
import sys 
sys.path.append( '/home/hroest/srm_clashes/code' )
sys.path.append( '/home/hroest/lib/' )
db = MySQLdb.connect(read_default_file="~/.my.cnf")
cursor = db.cursor()
import collider
import hlib
import copy



from optparse import OptionParser, OptionGroup
usage = "usage: %prog [options]"
parser = OptionParser(usage=usage)

group = OptionGroup(parser, "Spectral library Options", "")
group.add_option("--background", dest="background", default='',
                  help="A different background " )
parser.add_option_group(group)
par = collider.SRM_parameters()
par.parse_cmdl_args(parser)
options, args = parser.parse_args(sys.argv[1:])
#local arguments
background = options.background
par.__dict__.update( options.__dict__ )
par.parse_options(options)
if par.max_uis ==0: 
    print "Please change --max_uis option, 0 does not make sense here"
    sys.exit()

par.dontdo2p2f = False
par.do_1vs = False
par.eval()
print par.experiment_type
print par.get_common_filename()
par.query1_add += ' order by Intensity DESC' #only for the toptrans workflow

mycollider = collider.SRMcollider()
cmadd = par.peptide_table.split('.')[1]
#we need a different background for the peptide atlas
#because there we have differnt peptide_keys and cannot relate
#those with the MRMlink table
#only for peptide atlas since those peptide keys map to experiment 3452 and not
#to 3131 as we would need to then find the transition in the MRM table
#we only use the parbg for the calculations of the transitions. We still want 
if background != '':
    parbg = copy.deepcopy(par)
    parbg.transition_table = 'hroest.srmTransitions_' + background
    parbg.peptide_table = 'hroest.srmPeptides_' + background
    mycollider.find_clashes_toptrans_paola(db, par, bgpar=parbg)
    cmadd = parbg.peptide_table.split('.')[1]

else: mycollider.find_clashes_toptrans_paola(db, par) 

#calculate for precursor, peptide and protein the min nr transitions necessary
#to measure them without ambiguity
#create a new hroest.experiment
common_filename = par.get_common_filename()
query = """
insert into hroest.experiment  (name, short_description,
description, comment1, comment2, comment3, super_experiment_key, ddb_experiment_key)
VALUES (
    'paola 1Da/1Da', '%s', '%s', '%s', '%s', '%s', 3, 0
)
""" %( common_filename + '_' + cmadd, 
      par.experiment_type, par.peptide_table, par.transition_table, 
     'using new MRMAtlas_qtrap_final_no_pyroGlu')
cursor.execute(query)
myid = db.insert_id()

prepare = [ [p[0], p[1], myid]  for p in mycollider.min_transitions]
#save our result ("the min nr transitions per precursor") linked with 
#our new experiment key
cursor.executemany(
""" insert into hroest.result_srmpaola (parent_key, min_transitions, exp_key) 
    VALUES (%s,%s,%s) """, prepare
)


