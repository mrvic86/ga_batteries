import vt_ga
from pyexcel_ods import get_data
import time

def get_batts(filename):
    # Get data from file
    batts = []
    data = get_data(filename)
    batt_array = data['Sheet1']
    # Unpack into single list
    for line in batt_array:
        batts = batts + line

    return batts

def display_gene(gene, fitness, pack_size, battery_list):
    print 'Fitness Score: ', fitness
    for pk in range(pack_size['packs']):
        print 'Pack ', pk + 1
        for s in range(pack_size['series']):
            cap = 0
            for c in range(pack_size['paralell']):
                cap += battery_list[gene[pk][s][c]]
            print '  ', gene[pk][s], ' | Capacity: ', cap


# Init
iterations = 1000
pop_size = 1000
pack_size = {'series'  : 3,
             'paralell': 5,
             'packs'   : 6 }

filename = 'batts.ods'

# Get Battery Values
battery_list = get_batts(filename)
# Seed the population
start = time.time()
population = vt_ga.seed(battery_list, pop_size, pack_size)
# Rank
population_capacities, population_fitness = vt_ga.fitness(battery_list, population)
population, population_fitness = vt_ga.rank(population, population_fitness)

print population_fitness[0]
# for i in range(0,5):
#     print population[i]
# print '\n'

# Loop through each generation
for generation in range(1, iterations):
    start = time.time()
    # Populate this generation
    population = vt_ga.repopulate(population, pack_size, battery_list)
    # Rank
    population_capacities, population_fitness = vt_ga.fitness(battery_list, population)
    population, population_fitness = vt_ga.rank(population, population_fitness)

    print population_fitness[0]
    # for i in range(0,5):
    #     print population[i]
    # print '\n'

display_gene(population[0], population_fitness[0], pack_size, battery_list)
