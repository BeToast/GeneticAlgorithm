import random as rd
import matplotlib.pyplot as plt
import math
from re import findall
from copy import deepcopy


#defining a function that returns the average preferred lecturer that students have been assigned by the algorithm, per allocation.

def get_average_allocation(allocation,student_preferences):

    preferences=0
    #keeping track of where the lecturer was placed in the allocated student's preferences
    lect_preferences=[]
    
    #print("Getting average allocation preference")
    #loop through keys(lecturers), get lecturer's students and check where the lecturer placed in each the student's preference list.
    lecturers_list=list(allocation.keys())
    #print(lecturers_list)
    for i in range(len(lecturers_list)-1): #the -1 is to account for the presence of the "fitness" key in the allocation dict
        lecturer_index=str(lecturers_list[i]).split("lecturer")[1]
        students_allocated= allocation[lecturers_list[i]]["students"]
        #print("Students allocated for lecturer "+str(lecturer_index)+" are: ",students_allocated)

        if int(lecturer_index)<=9:
            lecturer_index="0"+str(lecturer_index)

        #loop through the students allocated to the lecturer
        for student in students_allocated:
            #print("Lecturer being considered is: ",lecturer_index)
            preferences+=student_preferences[student].index(int(lecturer_index))

        average=preferences/len(student_preferences)
    print("Average preference allocated to students in this allocation",average)

def quality_check(population) -> bool:
    fine = True
    for allocation in population:
        keys = list(allocation.keys())
        if "fitness" in keys: keys.remove("fitness")
        students_allocated = [item for sublist in [list((l, allocation[l]["students"])[1]) for l in keys] for item in sublist]
        missing = set(range(num_students))-set(students_allocated)
        conflict_set = set([student for student in students_allocated if students_allocated.count(student) > 1])
        if(len(set(students_allocated))!=46): 
            raise Exception("its broken")
            fine = False
    return fine


# completely random, does not repicate real scenario at all.
def random_student_preferences(num_students, num_lecturers):
    student_preferences = []
    for i in range(num_students):
        bingus= list(range(num_lecturers))
        rd.shuffle(bingus)
        student_preferences.append(bingus)
    del bingus # you deserve armageddon
    return student_preferences

# this function creates a allocation where a perfect fitness 0 is possible
def easy_student_preferences(num_lecturers, lecturer_capacties):
    student_preferences = []
    for lect_index in range(len(lecturer_capacties)):
        capacity = lecturer_capacties[lect_index]
        for _ in range(capacity):
            # currStudent=[lect_index]+list(set(range(num_lecturers))-set(lect_index))
            lecturers = list(range(num_lecturers))
            rd.shuffle(lecturers)
            lecturers.remove(lect_index)
            currStudent=[lect_index]+lecturers
            student_preferences.append(currStudent)
    return student_preferences

"""
get students who are assigned to lecturer
find index of lecturer in student_preferences[stduent]
fitness is the sum(of the index where the lectures is in student_preferences)
0 is best
"""
#function that returns the average fitness of the population (fitness of all the allocations summed/number of allocations)
def update_fitness_population(population, student_preferences): # returns average fitness
    sum_all_fitness=0
    for allocation in population:
        sum_all_fitness+=update_fitness(allocation, student_preferences)
    return sum_all_fitness/len(population)

def update_fitness(allocation, student_preferences):
    fitness = 0
    for i in range(len(allocation)-1): # fitness is first index.
        student_indexes = allocation["lecturer"+str(i)]["students"]
        '''
        student_indexes is a list of students assigned to lectuere [0,5]
        accesss studnet preferences for each student
        get index of lectuere in student_index
        '''
        lecturer_fitness = 0
        for index in student_indexes:
            lecturer_fitness += student_preferences[index].index(i)
        fitness += lecturer_fitness
    allocation["fitness"]=fitness
    return fitness


def calc_lecture_allocation_values(num_students, num_lecturers):
    min_allocations = math.floor(num_students/num_lecturers)
    num_excess = num_students%num_lecturers
    static_dna_values = [min_allocations]*num_lecturers
    return [3,1,2,3,1,2,2,2,1,4,1,1,2,2,3,1,2,1,1,4,4,3] #hard-coded in values from the excel spreadsheet.
    for i in range(num_excess):
        static_dna_values[i]+=1
    return static_dna_values
    

# randomly initialising the population
def initialise_population(pop_size, lecturer_capacties, student_preferences):
    population=[]
    for p in range(pop_size):
        population.append({})
        student_index_list=range(0,num_students)
        
        for i in range(0, num_lecturers):
            lecturer="lecturer"+str(i)
            curr_students = rd.sample(student_index_list,lecturer_capacties[i]) # get students equal to lecturer capacity
            
            population[p][lecturer] = {"capacity": lecturer_capacties[i], "students": curr_students}
            # population[allocation].update("f{lecturer}" : 
            student_index_list = list(set(student_index_list)-set(curr_students))

        population[p].update({"fitness":""})
        update_fitness(population[p], student_preferences)
    return population # returning a list of generated populations

# return lowest(best) fitness.
def fight(gladiators): #gladiators is a list of gladiators.
    currWinner = gladiators[0]
    for i in range(1, len(gladiators)):
        if gladiators[i]["fitness"] < currWinner["fitness"]:
            currWinner = gladiators[i]
    return currWinner

# returns strongest_gladiators(most fit) with size population/tournament_size
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


# The Mutation function
def mutate_population(population,mutate_chance,student_preferences):
    for allo_index in range(len(population)-1):
        allocation = population[allo_index]

        for lecturerIndex in range(len(allocation)-1):
            if rd.randint(0,1000)<mutate_chance:
                lecturer="lecturer"+str(lecturerIndex)
                lect_students=allocation[lecturer]["students"]
                #choosing the unhappier student
                students_ranking_of_lecturer=[]

                for student in lect_students: #student is a number like 0, 30 etc.
                    students_ranking_of_lecturer.append(student_preferences[student].index(lecturerIndex))

                #identifying the unhappiest student
                unhappy_student_index=students_ranking_of_lecturer.index(max(students_ranking_of_lecturer))
                unhappy_student=lect_students[unhappy_student_index]

                random_lecturer_index=rd.randint(0,len(allocation)-2)
                while random_lecturer_index==lecturerIndex:
                    random_lecturer_index=rd.randint(0,len(allocation)-2)
                #index of student to swap in the random lecturer
                student_in_random_lecturer_index = rd.randint(0,allocation["lecturer"+str(random_lecturer_index)]["capacity"]-1)

                allocation_debug=allocation
                # do the swap
                allocation[lecturer]["students"][unhappy_student_index] = allocation["lecturer"+str(random_lecturer_index)]["students"][student_in_random_lecturer_index]
                allocation["lecturer"+str(random_lecturer_index)]["students"][student_in_random_lecturer_index] = unhappy_student

        population[allo_index] = allocation
    return population

def cross_over_two_parents(allocation1, allocation2, num_lectures, num_students, student_preferences):
    temp=quality_check(population)

    keys = list(allocation1.keys())
    keys.remove("fitness")

    cross_over_index = rd.randint(0, num_lectures-1)
    slice_1_keys = keys[0:cross_over_index]
    slice_2_keys = keys[cross_over_index:num_lectures]

    alloc_1_first = deepcopy(dict((k, allocation1[k]) for k in slice_1_keys))
    alloc_1_second = deepcopy(dict((k, allocation1[k]) for k in slice_2_keys))
    alloc_2_first = deepcopy(dict((k, allocation2[k]) for k in slice_1_keys))
    alloc_2_second = deepcopy(dict((k, allocation2[k]) for k in slice_2_keys))

    temp=quality_check(population)
  
    child_one = {**alloc_1_first, **alloc_2_second}
    child_two = {**alloc_2_first, **alloc_1_second}
    # child_one = alloc_1_first.copy()
    # child_one.update(alloc_2_second)

    # child_two = alloc_2_first.copy()
    # child_two.update(alloc_1_second)

    temp=quality_check(population)

    child_1 = confict_resolution(child_one, keys, num_students, student_preferences)
    child_2 = confict_resolution(child_two, keys, num_students, student_preferences)

    temp2=quality_check(population)

    return [child_1, child_2]


def confict_resolution(child, keys, num_students, student_preferences):
    # temp=quality_check(population)
    debug_child = child
    # get an array of all allocated students
    # read this line, you filty casual...
    students_allocated = [item for sublist in [list((l, child[l]["students"])[1]) for l in keys] for item in sublist]
    # missing are students not allocated
    missing = set(range(num_students))-set(students_allocated)
    # where a student is double allocated
    conflict_set = set([student for student in students_allocated if students_allocated.count(student) > 1])
    # dict where each entry is student number and both lecturer keys it occurs in. ex. {{'5' : [lecturer4, lecturer19]}}
    conflict_dict = {}
    for num in conflict_set:
        lecturer_index_list = []
        for lecturer in keys:
            if(child[lecturer]["students"].count(num) > 0):
                lecturer_index_list.append(lecturer)
        conflict_dict.update({str(num):lecturer_index_list})

    # determine which lecturer the conflict student prefers for each conflict
    # temp=quality_check(population)
    for num in conflict_set:
        lects_str = conflict_dict[str(num)]
        lects_int = [int(findall("\d+",lects_str[0])[0]), int(findall("\d+",lects_str[1])[0])]
        curr_preferences = student_preferences[num]
        lectuer_1_rating = curr_preferences.index(lects_int[0])
        lectuer_2_rating = curr_preferences.index(lects_int[1])
        if(lectuer_1_rating<lectuer_2_rating):
            #conflict student prefers first lecturer
            curr_students = child[lects_str[1]]["students"] # so replace second lecturer with a missing student
            curr_students[curr_students.index(num)] = missing.pop() # get random student replacement
            child[lects_str[1]].update({"students": curr_students}) # update values
        else:
            #conflict student prefers second lecturer
            curr_students = child[lects_str[0]]["students"] # so replace first lecturer with a missing student
            curr_students[curr_students.index(num)] = missing.pop() # get random student replacement
            child[lects_str[0]].update({"students": curr_students}) # update values

    return child

# # The Cross-Over function that acts as a wrapper for the actual cross_over functionality
def cross_over(population, original_population_size, num_lecturers, num_students, student_preferences):
    children=[]
    needed_kids=original_population_size-len(population)
    passes=0
    while len(children) < needed_kids:

        rd.shuffle(population)
        
        for i in range(1, len(population), 2): #1,0 & 3 2 ...... 1,0 & 3,2 & 5,4
            #children.append( cross_over_two_parents(list(population[i], population[i+1]), dna_length) )
            #print(f"index1 is {i-1} and index2 is {i}")
            crossed_over=cross_over_two_parents(population[i-1], population[i], num_lecturers, num_students, student_preferences)
            children.extend(crossed_over)
            if len(children) >= needed_kids:
                return children

    return children ## actual children of the population


# Plot the fitness of the population versus the generations passed.
def generate_graph(fitness_list, length, title, x_axis, y_axis, min_adjective):
  
    plt.xlabel(x_axis)
    plt.ylabel(y_axis)
    plt.title(title)

    print(f"Min {min_adjective} fitness value identified: {min(fitness_list)}")

    generations=list(range(0,length))
    #for i in range (0,len(average_fitness_list)):
        #plt.plot(average_fitness_list[i],i,"-",marker="D")

    plt.plot(generations,fitness_list,"-",marker="D")
    plt.show()


################################################# hyperparamters
max_generations = 100
tenth_percentage_chance = 0 # tenth a percent to mutate so 10 = 1%
num_students = 46
num_lecturers = 22
lecturer_capacties = calc_lecture_allocation_values(num_students, num_lecturers)
student_preferences = easy_student_preferences(num_lecturers, lecturer_capacties)
dna_length=len(lecturer_capacties)
tournament_size = 2
num_original_population = 100
#################################################
generations_passed=0
average_fitness_list=[]
best_fitness_list=[]

population=initialise_population(num_original_population,lecturer_capacties, student_preferences)
population = sorted(population, key=lambda allocation: allocation['fitness'])
temp=quality_check(population)

get_average_allocation(population[0],student_preferences)

#the driver/evolution loop
while(generations_passed<max_generations):
    print(f"start generation {generations_passed}")
    winners=tournament_selection(tournament_size,population)
    population=winners
    population=sorted(population, key=lambda person: person['fitness'])
    temp=quality_check(population)

    #cross-over winners
    # print("cross-over start")
    children=cross_over(population, num_original_population, num_lecturers, num_students, student_preferences)
    quality_check(population)

    # #print("Kids returned:",len(children))
    
    # add their kids back into population  
    for child in children:
        population.append(child)
    temp=quality_check(population)

    # print("Population after kids",len(population))
    # mutate population
    # print("start mutation")
    population = mutate_population(population,tenth_percentage_chance,student_preferences)
    temp=quality_check(population)

    average_fitness_list.append(update_fitness_population(population,student_preferences))
    population = sorted(population, key=lambda allocation: allocation['fitness'])
    best_fitness_list.append(population[0]['fitness'])
    temp=quality_check(population)

    ##increase generations_passed
    generations_passed+=1

    #if perfect fitness then break or max_generations reached break
    if(best_fitness_list[-1]==0): #if convergence has been reached, break out of the loop
        print(f"Converged!")
        break

population = sorted(population, key=lambda allocation: allocation['fitness'])
print(f"generations_passed={generations_passed}\nbest_dna={population[0]['fitness']}")
generate_graph(average_fitness_list,len(average_fitness_list), "Plotting average fitness of population against Generations passed","Generations Passed", "Average Fitness of Population", "average")
generate_graph(best_fitness_list,len(average_fitness_list), "Plotting best fitness of population against Generations passed", "Generations Passed", "Best Fitness of Population", "")