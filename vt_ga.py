import statistics
import random
import math
import copy

def fitness(batteries, population):
    population_fitness = []
    population_capacities = []

    # Loop through each pack and work look at each series SD
    for packs in population:
        pack_capacities = []
        pack_sds = []

        for pack in packs:
            series = []
            for paralell in pack:
                paralell_sum = 0
                for cell in paralell:
                    paralell_sum += batteries[cell]
                series.append(paralell_sum)

            pack_capacities.append(series)
            pack_sds.append(statistics.stdev(series))

        # Add each pack SD to a weighted all pack SD
        population_fitness.append(sum(pack_sds) + 10*statistics.stdev(pack_sds))
        population_capacities.append(pack_capacities)

    return population_capacities, population_fitness

def seed(batteries, pop_size, pack_size):
    # Create the blank full population list
    pop = [[[ [0 for a in range(pack_size['paralell']) ]
                 for b in range(pack_size['series']) ]
                 for c in range(pack_size['packs']) ]
                 for d in range(pop_size) ]
    number_of_batts = len(batteries)

    # Loop through and random populate every gene
    for g in range(0,pop_size):
        batt_used = [False] * number_of_batts
        for pk in range(pack_size['packs']):
            for s in range(pack_size['series']):
                for c in range(pack_size['paralell']):
                    cell = random.randint(0, number_of_batts-1)
                    pop[g][pk][s][c] = cell

        # Fix each gene to remove duplicates
        pop[g] = fixgene(pop[g], batteries)

    return pop

def fixgene(gene, batts):
    # Check to see how many times each cell has been used
    count = [0 for a in range(len(batts)) ]
    locations = [[] for a in range(len(batts)) ]
    for pk, pack in enumerate(gene):
        for s, series in enumerate(pack):
            for c, cell in enumerate(series):
                count[cell] += 1
                locations[cell] = locations[cell] + [[pk, s, c]]

    max_value = max(count)
    max_index = count.index(max_value)

    # If cell used more than once then fix
    while max_value > 1:
        # Find where in gene a duplicate is
        [pk, s, c] = locations[max_index][0]
        # Find a cell that's not used
        min_index = count.index(0)
        gene[pk][s][c] = min_index
        # Make the swap from duplicate to unused and update counters
        count[max_index] -= 1
        count[min_index] += 1
        locations[max_index].pop(0)
        max_value = max(count)
        max_index = count.index(max_value)
        if min(count) < 1 :
            min_index = count.index(0)

    return gene

def repopulate(population, pack_size, batteries):
    # Where in population to keep
    percentage_to_keep = 0.3
    pop_size = len(population)
    number_of_keepers = int(round(pop_size*percentage_to_keep))
    to_breed = round_up_to_even(number_of_keepers/2)
    to_mutate = number_of_keepers - to_breed
    remainder = pop_size - to_breed - to_mutate
    # for i in range(0,pop_size):
    #     print population[i]
    # print '\n'

    # Where in population to replace
    breed_start = to_mutate + to_breed
    breed_stop = breed_start + int(round(remainder/2) - 1)
    mutate_start = breed_stop + 2
    mutate_stop = pop_size
    # print breed_start, breed_stop, mutate_start, mutate_stop

    # Loop through population to replace with breeders
    seed_gene = 0
    for i in range(breed_start, breed_stop):
        population[i] = breed(population[seed_gene], population[seed_gene + 1], pack_size)
        population[i] = fixgene(population[i], batteries)
        # print 'Breeding gene ', i, ' from ', seed_gene, ' & ', seed_gene+1
        seed_gene += 2
        if seed_gene >= to_breed: seed_gene = 0

    # Loop through population to replace with mutations
    seed_gene = to_breed
    for i in range(mutate_start,mutate_stop):
        population[i] = mutate(population[seed_gene], pack_size, batteries)
        population[i] = fixgene(population[i], batteries)
        # print 'Mutating gene ', i, ' with ', seed_gene
        seed_gene += 1
        if seed_gene >= number_of_keepers: seed_gene = to_breed

    # Remove any duplicate entries
    population = remove_duplicates(population, pop_size, batteries, pack_size)
    # for i in range(0,pop_size):
    #     print population[i]
    # print '\n'
    return population

def mutate(gene, pack_size, batteries):
    newgene = copy.deepcopy(gene)
    # Mutate between 1 to 3 cells
    no_of_muations = random.randint(1,3)

    # Loop through and do each mutation
    for m in range(no_of_muations):
        p = random.randint(0,pack_size['packs']-1)
        s = random.randint(0,pack_size['series']-1)
        c = random.randint(0,pack_size['paralell']-1)

        number_of_batts = len(batteries)
        newgene[p][s][c] = random.randint(0, number_of_batts-1)

    return newgene

def breed(gene1, gene2, pack_size):
    newgene = copy.deepcopy(gene1)
    # Random determine where to cut genes
    p_cut = random.randint(0,pack_size['packs']-1)
    s_cut = random.randint(0,pack_size['series']-1)
    c_cut = random.randint(0,pack_size['paralell']-1)

    # Setup when we've looped to cut point
    p_reached = False
    s_reached = False
    c_reached = False

    # Loop through and copy first part of gene1 and 2nd part of gene2
    for pk in range(pack_size['packs']):
        if pk >= p_cut: p_reached = True
        for s in range(pack_size['series']):
            if s >= s_cut: s_reached = True
            for c in range(pack_size['paralell']):
                if c >= c_cut: c_reached = True

                if p_reached and s_reached and c_reached:
                    newgene[pk][s][c] = gene2[pk][s][c]
                else:
                    newgene[pk][s][c] = gene1[pk][s][c]

    return newgene

def rank(population, fitness):
    # Get index ranking
    index = range(len(fitness))
    index.sort(key = fitness.__getitem__)

    # Re-arrange lists
    fitness[:] = [fitness[i] for i in index]
    population[:] = [population[i] for i in index]

    return population, fitness

def remove_duplicates(list, pop_size, batteries, pack_size):
    final_list = []
    for num in list:
        if num not in final_list:
            final_list.append(num)

    missing = pop_size - len(final_list)
    final_list = final_list + seed(batteries, missing, pack_size)
    return final_list

def round_up_to_even(f):
    return int(math.ceil(f / 2.) * 2)

# # Test Routine common
# test_bats = [11,10,12,11,16,13,12,14]
# #            S, P, Packs
# pack_size = {'series'  : 2,
#              'paralell': 2,
#              'packs'   : 2 }
#
# # population[ packs[ pack[ series[ paralell]  ] ] ]
# test_pop = [ [ [[1,3],[5,2]], [[4,7],[0,6]] ],
#              [ [[1,2],[4,3]], [[0,7],[5,6]] ] ]
#
# test_pop = seed(test_bats, 10, pack_size)
# print fitness(test_bats, test_pop)
#
# print test_pop[0]
# print mutate(test_pop[0], pack_size, test_bats)

# print test_pop
# print breed(test_pop[0],test_pop[1], pack_size)
