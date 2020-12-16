def getProductionsMax(prods, nterms):
  nouse = ['+', '-', 'or', 'not', 'and', '>=', '=']
  for nterm in nterms:
    print("nterm:", nterm)
    if type(nterm) == tuple or (type(nterm) == list and nterm[0] in nouse):
      continue
    print("nterm used:", nterm)
    if type(nterm) == tuple:
      prods.append(str(nterm[1]))
    else:
      prods.append(nterm)
