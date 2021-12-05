


#                                   PROJET MOGPL 2021 GROUPE 3
#                                             GRAPHES
#                                  KRISNI Almehdi et ABREU Hugo
#                          https://github.com/krisninho2000/Projet_MOGPL


#######################################################################################################
# LIBRAIRIES PYTHON
#######################################################################################################

import numpy as np
from gurobipy import *
import algorithmesChemin
import util as ut

#######################################################################################################
# PROGRAMME D'OPTIMISATION
#######################################################################################################

# Méthode permettant de réaliser l'optimisation du problème de plus court chemin
def optPlusCourtChemin(graphe ,start, end) :
    # On récupère la liste des différents sommets du graphe
    sommets = list(graphe.keys())
    nbSommets = len(sommets)

    # Le dictionnaire 'index' nous permettra de connaître l'indice de chaque sommet du graphe
    index = dict()
    for i in range(nbSommets) :
        index[sommets[i]] = i

    # On crée la matrice de présence des arcs
    link = []
    for i in sommets :
        tempLink = [0 for _ in range(nbSommets)]
        for j in sommets :
            if (j in graphe[i]) :
                tempLink[index[j]] = 1
        link.append(tempLink)

    # On crée la matrice des contraintes
    # Les indices représentent les sommets
    a = []

    # On crée la matrice des seconds membres
    b = []

    # Règles de résolution du problème
    # L'optimisation est réalisée sur le base de contraintes

    # Contraitre 1 - Il n'y a qu'une seule et unique arête sortante depuis le sommet de départ
    # Il s'agit d'une contrainte de type A = B
    cont1 = [link[index[start]][i] for i in range(nbSommets)]

    # On met à jour la matrice des contraintes et la matrice des seconds membres
    b += [1]
    a += [cont1]



    # Contrainte 2 - Il n'y a qu'une seule et unique arête entrante sur le sommet d'arrivée
    # Il s'agit d'une contrainte de type A = B
    cont2 = [link[i][index[end]] for i in range(nbSommets)]

    # On met à jour la matrice des contraintes et la matrice des seconds membres
    b += [1]
    a += [cont2]

    # Contrainte 3 - Il existe au plus une seule arête sortante depuis un sommet s
    # Il s'agit d'une contrainte de forme A <= B
    cont3 = []

    for i in range(nbSommets) :
        tempC = [link[i][j] for j in range(nbSommets)] # Liste des arcs sortants du sommet i (soit le sommet s) vers les sommets j
        cont3.append(tempC)
        b += [1] # On met à jour le second membre

    # On met à jour la matrice des contraintes et la matrice des seconds membres
    a += cont3



    # Contrainte 4 - Il existe au plus une seule arête entrante vers un sommet s
    # Il s'agit d'une contrainte de forme A <= B
    cont4 = []

    for j in range(nbSommets) :
        tempC = [link[i][j] for i in range(nbSommets)] # Liste des arcs sortants du sommet i vers le sommet j (soit le sommet s)
        cont4.append(tempC)
        b += [1]

    # On met à jour la matrice des contraintes et la matrice des seconds membres
    a += cont4



    # On crée le modèle
    m = Model("optCheminPlusCourt")

    # On crée les coefficients allant servir pour la fonction objectif
    c = [link[i][j] for i in range(nbSommets) for j in range(nbSommets)]

    # On crée la liste des variables
    x = [] # Représente la liste des variables
    for i in range(nbSommets) :
        for j in range(nbSommets) :
            x.append(m.addVar(vtype=GRB.BINARY, lb=0, name = "Arc_%s,%s" % (sommets[i], sommets[j]))) # La variable (i,j) représente l'arc allant du sommet i au sommet jS

    # On met à jour le modèle
    m.update()

    # On crée la fonction objectif
    obj = LinExpr()
    obj = 0
    for i in range(nbSommets * nbSommets) :
        obj += c[i] * x[i] # La fonction objectif ne prend donc en compte que les arcs existants dans le graphe (grâce aux coefficients)

    # On définit le choix d'optimisation de l'objectif (MAXIMIZE ou MINIMIZE)
    m.setObjective(obj, GRB.MAXIMIZE)

    print("\n\n\n")

    # On définit les contraintes
    # Les contraintes suivront toujours l'ordre suivant
    # Les deux premières sont à l'égalite
    # Le reste sont à l'inférieur
    for i in range(len(b)) : # len(b) = nombre de contraintes
        if (i < 2) : # Contraintes à l'égalite
            if (i == 0) : # Contrainte 1
                m.addConstr(quicksum(a[i][j] * x[index[start] * (nbSommets - 1) + j] for j in range(nbSommets)) == b[i], "Contrainte " + str(i))

            else : # Contrainte 2
                m.addConstr(quicksum(a[i][j] * x[index[end] + (nbSommets) * j] for j in range(nbSommets)) == b[i], "Contrainte " + str(i))

        else : # Contraintes à l'infériorité
            # 
            if (i < len(b) - nbSommets) : # Contrainte 3
                k = (i - 2) % nbSommets
                m.addConstr(quicksum(a[i][j] * x[int(k * (nbSommets) + j)] for j in range(nbSommets)) <= b[i], "Contrainte " + str(i))

                # print([a[i][j] * x[int(k * (nbSommets) + j)] for j in range(nbSommets)])
            
            else : # Contrainte 4
                k = (i - 2) % nbSommets
                m.addConstr(quicksum(a[i][j] * x[int(j * (nbSommets) + k)] for j in range(nbSommets)) <= b[i], "Contrainte " + str(i))

                print([a[i][j] * x[int(j * (nbSommets) + k)] for j in range(nbSommets)])


    print("\n\n\n")

    # On effectue la résolution
    m.optimize()

    print([(v.varName, v.X) for v in m.getVars() if abs(v.obj) > 1e-6])

    if m.status == GRB.OPTIMAL:
        print()
        print('Optimal objective: %g' % m.objVal)
        print()
    if m.status == GRB.INF_OR_UNBD:
        print('Model is infeasible or unbounded')
        sys.exit(0)
    if m.status == GRB.INFEASIBLE:
        print('Model is infeasible')
        sys.exit(0)
    if m.status == GRB.UNBOUNDED:
        print('Model is unbounded')
        sys.exit(0)
    else:
        print('Optimization ended with status %d' % m.status)
        sys.exit(0)

#######################################################################################################
# PARTIE TEST
#######################################################################################################

g = ut.acquisitionGraphe("Repertoire_Graphes/exempleGraphe.txt")
g = ut.transformeGrapheCondense(g)
optPlusCourtChemin(g, 'a', 'k')