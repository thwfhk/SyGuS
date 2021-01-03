Function to Synthesize: 
['synth-fun',
 'max2',
 [['x', 'Int'], ['y', 'Int']],
 'Int',
 [['Start',
   'Int',
   ['x', 'y', ('Int', 0), ('Int', 1), ['ite', 'StartBool', 'Start', 'Start']]],
  ['StartBool',
   'Bool',
   [['<=', 'Start', 'Start'],
    ['=', 'Start', 'Start'],
    ['>=', 'Start', 'Start']]]]]

Productions:
My-Start-Symbol  ->  ['Start']
Start  ->  ['x', 'y', '0', '1', ['ite', 'StartBool', 'Start', 'Start']]
StartBool  ->  [['<=', 'Start', 'Start'], ['=', 'Start', 'Start'], ['>=', 'Start', 'Start']]

# ------------------------------------------------------------------------

Extending [['ite', 'StartBool', 'Start', 'Start']]
Extended:
[['ite', ['<=', 'Start', 'Start'], 'Start', 'Start']]
[['ite', ['=', 'Start', 'Start'], 'Start', 'Start']]
[['ite', ['>=', 'Start', 'Start'], 'Start', 'Start']]
[['ite', 'StartBool', 'x', 'Start']]
[['ite', 'StartBool', 'y', 'Start']]
[['ite', 'StartBool', '0', 'Start']]
[['ite', 'StartBool', '1', 'Start']]
[['ite', 'StartBool', ['ite', 'StartBool', 'Start', 'Start'], 'Start']]
[['ite', 'StartBool', 'Start', 'x']]
[['ite', 'StartBool', 'Start', 'y']]
[['ite', 'StartBool', 'Start', '0']]
[['ite', 'StartBool', 'Start', '1']]
[['ite', 'StartBool', 'Start', ['ite', 'StartBool', 'Start', 'Start']]]
