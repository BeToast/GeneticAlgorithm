import random as rd
import matplotlib.pyplot as plt
import math
import operator

# def calc_fitness(dna, target):
#     score=0
#     if dna == '0'*len(dna):
#         return 2*len(dna)

#     for i in range(0, len(dna)):
#         if dna[i]==target[i]:
#             score+=1
#     return score

def random_student_preferences(num_students, num_lecturers):
    student_preferences = []
    for i in range(num_students):
        bingus= list(range(num_lecturers))
        rd.shuffle(bingus)
        student_preferences.append(bingus)
    del bingus # you deserve armageddon
    return student_preferences


"""
get students who are assigned to lecturer
find index of lecturer in student_preferences[stduent]
fitness is the sum(of the index where the lectures is in student_preferences)
0 is best
"""


def update_fitness(allocation_dict, student_preferences):
    fitness = 0
    for i in range(len(allocation_dict)-1): # fitness is first index.
        student_indexes = allocation_dict["lecturer"+str(i)]["students"]
        '''
        student_indexes is a list of students assigned to lectuere [0,5]
        accesss studnet preferences for each student
        get index of lectuere in student_index
        '''
        lecturer_fitness = 0
        for index in student_indexes:
            lecturer_fitness += student_preferences[index].index(i)
        fitness += lecturer_fitness
    return fitness


# def convergence(population,optimal_dna):
#     for person in population:
#         if(person["dna"]==optimal_dna):
#             return 1

#     return 0

def calc_lecture_allocation_values(num_students, num_lecturers):
    min_allocations = math.floor(num_students/num_lecturers)
    num_excess = num_students%num_lecturers
    static_dna_values = [min_allocations]*num_lecturers
    for i in range(num_excess):
        static_dna_values[i]+=1
    return static_dna_values

# ##randomly initialising the population
def initialise_population(pop_size, lecturer_capacties, student_preferences):
    population=[]
    for p in range(pop_size):
        population.append({})
        student_index_list=range(0,num_students)
        rd.shuffle(lecturer_capacties) # shuffle what lecturers get what capatitcy
        
        for i in range(0, num_lecturers):
            lecturer="lecturer"+str(i)
            curr_students = rd.sample(student_index_list,lecturer_capacties[i]) # get students equal to lecturer capacity
            
            population[p][lecturer] = {"capacity": lecturer_capacties[i], "students": curr_students}
            # population[allocation].update("f{lecturer}" : 
            student_index_list = list(set(student_index_list)-set(curr_students))

        population[p].update({"fitness":""})
        population[p].update({"fitness":update_fitness(population[p].copy(), student_preferences)})
    return population # returning a list of generated populations


# #a "fight" is just fitness of x vs fitness of y. The gladiator with greater fitness "wins"
# #winner moves on to the next generation. Losers?

def fight(gladiators): #gladiators is a list of gladiators.
    currWinner = gladiators[0]
    for i in range(1, len(gladiators)):
        if gladiators[i]["fitness"] < currWinner["fitness"]:
            currWinner = gladiators[i]
    return currWinner

# #returns strongest_gladiators with size population/tournament_size
def tournament_selection(tournament_size,population):
    # lectures are gladiatores for flavour
    strongest_gladiators=[]
    num_fights=round(len(population)/tournament_size)
    for i in range(0, num_fights):

        #giving fighters a pass
        if (len(population)<tournament_size):
            #strongest_gladiators.append(population)
            #this^ was returning an array of gladiators, rather than appending each individually.
            #so then it would not be able to find the 'dna' attribute of a list later on.
            for p in population:
                strongest_gladiators.append(p)
            return strongest_gladiators

        #print("Before fight",len(population))
        
        #randomly choosing tournament_size fighters to fight
        gladiators_to_fight=rd.sample(population,tournament_size)

        #getting the winner of the fight and adding him to winners list
        strongest_gladiators.append(fight(gladiators_to_fight)) 

        #remove combatants from population
        for gladiator in gladiators_to_fight:
            population.remove(gladiator)

    return strongest_gladiators


# #The Mutation function

def swap_mutation(population,tenth_percentage_chance):
    for person in population:
        for i in range(0,len(person["dna"])):
            if(rd.randint(0,1000)<tenth_percentage_chance): #chance to swap mutate. (multiple mutations for one dna is possible)
                indexToSwap = range(0, person["dna"])
                buffer = person["dna"][i]
                person["dna"][i] = person["dna"][indexToSwap]
                person["dna"][indexToSwap] = buffer


# #The Cross-over function that generates kids
# def cross_over_two_parents(parent1, parent2, dna_length, optimal_dna):
    
#     dna_parent_one=parent1['dna']
#     dna_parent_two=parent2['dna']
#     cross_over_index = rd.randint(0, dna_length-1)
#     slice_one = slice(cross_over_index)
#     slice_two = slice(cross_over_index, dna_length)

#     children = []

#     ###NOTE: @Blake, shouldn't each Child be a gladiator object?. They just can't be strings. I've made the change

#     #children.append(dna_parent_one[slice_one]+dna_parent_two[slice_two])
#     #children.append(dna_parent_two[slice_one]+dna_parent_one[slice_two])
#     dna_child1=str(dna_parent_one[slice_one])+str(dna_parent_two[slice_two])
#     dna_child2=str(dna_parent_two[slice_one])+str(dna_parent_one[slice_two])
    
#     child1={"dna":dna_child1,"fitness":calc_fitness(dna_child1, optimal_dna),"losses":0, "wins":0}
#     child2={"dna":dna_child2,"fitness":calc_fitness(dna_child2, optimal_dna),"losses":0, "wins":0}

#     children.append(child1)
#     children.append(child2)
    
#     return children

# # The Cross-Over function that acts as a wrapper for the actual cross_over functionality
# def cross_over(population, dna_length, original_population_size):
#     children=[]
#     needed_kids=original_population_size-len(population)
#     passes=0
#     while len(children) < needed_kids:
#         # if passes%2==0: #alternate between order by fitness and randomness
#         #     #population = sorted(population, key=lambda person: person["fitness"], reverse=True) #sort by fitness
#         #     population.sort(key=lambda person: person["fitness"], reverse=True)
#         #     passes+=1
#         # else:
#         #     rd.shuffle(population) #randomly re-order list
#         #     passes+=1

#         rd.shuffle(population)
        
#         for i in range(1, len(population), 2): #1,0 & 3 2 ...... 1,0 & 3,2 & 5,4
#             #children.append( cross_over_two_parents(list(population[i], population[i+1]), dna_length) )
#             #print(f"index1 is {i-1} and index2 is {i}")
#             crossed_over=cross_over_two_parents(population[i-1], population[i], dna_length, optimal_dna)
#             children.extend(crossed_over)
#             if len(children) >= needed_kids:
#                 return children

#     return children ## actual children of the population


# #Plot the average fitness of the population versus the generations passed.
# def generate_graph(average_fitness_list, length, title, x_axis, y_axis):
  
#     plt.xlabel(x_axis)
#     plt.ylabel(y_axis)
#     plt.title(title)

#     print(f"Max average fitness value identified: {max(average_fitness_list)}")

#     generations=list(range(0,length))
#     #for i in range (0,len(average_fitness_list)):
#         #plt.plot(average_fitness_list[i],i,"-",marker="D")

#     plt.plot(average_fitness_list,generations,"-",marker="D")
#     plt.show()


################################################# hyperparamters
max_generations=100
tenth_percentage_chance=10 # tenth a percent to mutate so 10 = 1%
num_students = 46
num_lecturers = 22
lecturer_capacties=calc_lecture_allocation_values(num_students, num_lecturers)
student_preferences = random_student_preferences(num_students, num_lecturers)
dna_length=len(lecturer_capacties)
tournament_size=2
num_original_population=100
#################################################
generations_passed=0
average_fitness_list=[]
best_fitness_list=[]

population=initialise_population(num_original_population,lecturer_capacties, student_preferences)
population=sorted(population, key=lambda person: person['fitness'])

#the driver/evolution loop
while(generations_passed<max_generations):
    winners=tournament_selection(tournament_size,population)
    population=winners
    population=sorted(population, key=lambda person: person['fitness'])
    
    #cross-over winners
    children=cross_over(population,dna_length,num_original_population)

    #print("Kids returned:",len(children))
    
    ##add their kids back into population  
    for child in children:
        population.append(child)

    #print("Population after kids",len(population))
    #mutate population
    population=mutation(population, chance_to_mutate)

    average_fitness_list.append(update_fitness(population, optimal_dna))
    population = sorted(population, key=lambda person: person['fitness'], reverse=True)
    best_fitness_list.append(population[0]['fitness'])

    ##increase generations_passed
    generations_passed+=1

    #if perfect fitness then break or max_generations reached break
    
    if(convergence(population,optimal_dna)): #if convergence has been reached, break out of the loop
        print(f"Converged!")        
        break

population = sorted(population, key=lambda person: person['fitness'], reverse=True)
print(f"generations_passed={generations_passed}\nbest_dna={population[0]['dna']}")
generate_graph(average_fitness_list,len(average_fitness_list), "Plotting average fitness of population against Generations passed", "Average Fitness of Population","Generations Passed")
generate_graph(best_fitness_list,len(average_fitness_list), "Plotting best fitness of population against Generations passed", "Best Fitness of Population","Generations Passed")