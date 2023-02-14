import random as rd
import matplotlib.pyplot as plt
import math
from re import findall
from copy import deepcopy
import openpyxl


#defining a function that returns the average preferred lecturer that students have been assigned by the algorithm, per allocation.
def get_average_allocation(allocation,student_preferences):
    
    preferences=0
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
    #print("Average preference allocated to students in this allocation",average)
    return average

def quality_check(population) -> bool:
    fine = True
    for allocation in population:
        keys = list(allocation.keys())
        if "fitness" in keys: keys.remove("fitness")
        students_allocated = [item for sublist in [list((l, allocation[l]["students"])[1]) for l in keys] for item in sublist]
        missing = set(range(num_students))-set(students_allocated)
        conflict_set = set([student for student in students_allocated if students_allocated.count(student) > 1])
        if(len(set(students_allocated))!=46): 
            fine = False
            print("Allocated: ",students_allocated)
            print("Missing: ",missing)
            print("Conflict set: ",conflict_set )
            raise Exception("its broken")
    return fine




#--------------------------------------------Functions to get input data (lecturer capacities and student preferences)------------------------
def get_lecturer_capacities():

    # return [3,1,2,3,1,2,2,2,1,4,1,1,2,2,3,1,2,1,1,4,4,3] #hard-coded in values from the excel spreadsheet.
    
    lecturer_capacities=[]

    workbook = openpyxl.load_workbook("Supervisors.xlsx")
    worksheet = workbook.active
        
    for row in worksheet.values:
        for column in row:
            
            if(type(column)==str): #ensuring that strings like "Supervisor" are not read
                continue
            else:
                lecturer_capacities.append(column)
            
    print("lecturer capacities are: ",lecturer_capacities)

    return lecturer_capacities

def get_student_preferences():
    student_preferences=[]

    workbook = openpyxl.load_workbook("Student-choices.xlsx")
    worksheet = workbook.active
        
    for row in worksheet.values:
        lecturer_num = -1
        student_prefs=[0]*22
        for column in row:
            if(type(column)==str): #ensuring that strings like "Supervisor" or "Student" are not read
                #print(column)
                continue
            else:
                lecturer_num+=1
                student_prefs[column-1]=lecturer_num
        student_preferences.append(student_prefs)

    #print("Student 46's preferences : ",student_preferences[45])
    
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
fitness is the sum(of the index where the lecturer is in student_preferences)
0 is best
"""
#--------------------------------------------GA OPERATOR FUNCTIONS --------------------------------------------------------------

#function that returns the average fitness of the population (fitness of all the allocations summed/number of allocations)
def update_fitness_population(population, student_preferences): # returns average fitness
    sum_all_fitness=0
    for allocation in population:
        sum_all_fitness+=update_fitness(allocation, student_preferences)
    return sum_all_fitness/len(population)

# The fitness function
def update_fitness(allocation, student_preferences):
    fitness = 0
    for i in range(len(allocation)-1):  #accounting for lecturer starting with 1 here
        student_indexes = allocation["lecturer"+str(i)]["students"]
        '''
        student_indexes is a list of students assigned to lectuere [0,5]
        accesss studnet preferences for each student
        get index of lectuere in student_index
        '''
        lecturer_fitness = 0
        for index in student_indexes:
            lecturer_fitness += student_preferences[index].index(i) #NOTE: @BLAKE WE HAVE TO ACCOUNT FOR LECTURER 0 NOT BEING THERE
        fitness += lecturer_fitness
    allocation["fitness"]=fitness
    return fitness
    

# randomly initialising the population
def initialise_population(pop_size, lecturer_capacties, student_preferences):
    population=[]
    for p in range(pop_size):
        population.append({})
        student_index_list=range(0,num_students)
        
        for i in range(0, num_lecturers):#accounting for lecturer starting with 1 here: MAJOR ACCOUNTING
            lecturer="lecturer"+str(i)
            curr_students = rd.sample(student_index_list,lecturer_capacties[i-1]) # get students equal to lecturer capacity
            
            population[p][lecturer] = {"capacity": lecturer_capacties[i-1], "students": curr_students}
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

    is_allocation_valid_before_mutation=quality_check(population)
    #for every allocation in the population
    for allo_index in range(len(population)-1):
        allocation = population[allo_index]

        #go through all lectures in an allocation, get their students
        for lecturerIndex in range(1,len(allocation)-1): #accounting for lecturer starting with 1 here

            #mutation has a (mutate_chance/1000)*100 chance of happening 
            if rd.randint(0,1000)<mutate_chance:
                lecturer="lecturer"+str(lecturerIndex)

                #obtaining the students allocated to the lecturer who is being mutated.
                lect_students=allocation[lecturer]["students"]

                #choosing the unhappier student
                students_ranking_of_lecturer=[] #[student1,student5]

                for student in lect_students: #student is a number like 0, 30 etc.

                    #getting an integer that represents where the student ranked this lecturer.
                    # lets say student 1 ranked this lecturer 7th and student 5 ranked this lecturer 10th
                    students_ranking_of_lecturer.append(student_preferences[student].index(lecturerIndex))
                    #students_ranking_of_lecturer=[7,10]
                    

                #identifying the unhappiest student
                #max value of students_ranking_of_lecturer is 10, which is in index 1 (2nd student in the allocated student list)
                unhappy_student_index=students_ranking_of_lecturer.index(max(students_ranking_of_lecturer))

                #acts as the temp variable in the swap
                unhappy_student=lect_students[unhappy_student_index]

                #choose a random lecturer WITHIN this allocation to swap the unhappy student with
                random_lecturer_index=rd.randint(1,len(allocation)-2) #accounting for lecturer starting with 1 here
                while random_lecturer_index==lecturerIndex:
                    random_lecturer_index=rd.randint(1,len(allocation)-2) #accounting for lecturer starting with 1 here

                #index of a random student to swap in the random lecturer
                student_in_random_lecturer_index = rd.randint(0,allocation["lecturer"+str(random_lecturer_index)]["capacity"]-1)

                allocation_debug=allocation

                # do the swap
                allocation[lecturer]["students"][unhappy_student_index] = allocation["lecturer"+str(random_lecturer_index)]["students"][student_in_random_lecturer_index]
                allocation["lecturer"+str(random_lecturer_index)]["students"][student_in_random_lecturer_index] = unhappy_student

        population[allo_index] = allocation

    is_allocation_valid_after_mutation=quality_check(population)
    return population

def cross_over_two_parents(allocation1, allocation2, num_lectures, num_students, student_preferences):
    temp=quality_check(population)

    #getting the list of lecturers in allocation 1 (should be the same in allocation 2 as well as lecturers are constant in allocations)
    keys = list(allocation1.keys())
    keys.remove("fitness")

    #choosing a random point to split the allocation in half.
    cross_over_index = rd.randint(0, num_lectures-1)
    #splitting the lecturers into two halves
    slice_1_keys = keys[0:cross_over_index]
    slice_2_keys = keys[cross_over_index:num_lectures]


    alloc_1_first = deepcopy(dict((k, allocation1[k]) for k in slice_1_keys))
    alloc_1_second = deepcopy(dict((k, allocation1[k]) for k in slice_2_keys))
    alloc_2_first = deepcopy(dict((k, allocation2[k]) for k in slice_1_keys))
    alloc_2_second = deepcopy(dict((k, allocation2[k]) for k in slice_2_keys))

    temp=quality_check(population)
  
    #children will maintain having 22 lecturers as their length.
    child_one = {**alloc_1_first, **alloc_2_second}
    child_two = {**alloc_2_first, **alloc_1_second}

    temp=quality_check(population)

    #dealing with possible missing/duplicated students, if any in the created child allocations.
    child_1 = confict_resolution(child_one, keys, num_students, student_preferences)
    child_2 = confict_resolution(child_two, keys, num_students, student_preferences)

    temp2=quality_check(population)

    return [child_1, child_2]

#function that deals with duplicate and missing students, as a result of crossover
def confict_resolution(child, keys, num_students, student_preferences):
    # temp=quality_check(population)
    debug_child = child
    # get an array of all allocated students
    # getting a list of all the allocated students by making a flat list
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
    #how many kids need to be made to keep population stable at original_population_size
    needed_kids=original_population_size-len(population)

    while len(children) < needed_kids:
        #so the population is shuffled for diverse parentage.
        rd.shuffle(population)
        
        #skipping 2, to get different parentage
        for i in range(1, len(population), 2): #1,0 & 3 2 ...... 1,0 & 3,2 & 5,4
            #children.append( cross_over_two_parents(list(population[i], population[i+1]), dna_length) )
            #print(f"index1 is {i-1} and index2 is {i}")
            crossed_over=cross_over_two_parents(population[i-1], population[i], num_lecturers, num_students, student_preferences)
            children.extend(crossed_over)
            if len(children) >= needed_kids:
                return children

    return children ## actual children of the population

#--------------------------------------------Function to graph the output----------------------------------------------------------------
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


#--------------------------------------------DRIVER CODE--------------------------------------------------------------------------


################################################# hyperparameters
max_generations = 100
tenth_percentage_chance = 20 # tenth a percent to mutate so 10 = 1%
num_students = 46
num_lecturers = 22
lecturer_capacties = get_lecturer_capacities()
student_preferences = get_student_preferences()
dna_length=len(lecturer_capacties)
tournament_size = 2
num_original_population = 100
#################################################
generations_passed=0
average_fitness_list=[]
best_fitness_list=[]
do_tournament_selection = True
generations_since_big_mutation = 0

#Initialising pseudo-random population consisting of multiple random allocations based on imported capacities and preferences
population=initialise_population(num_original_population,lecturer_capacties, student_preferences)

#sort based on initial fitness of the population
population = sorted(population, key=lambda allocation: allocation['fitness'])
temp=quality_check(population)


#the driver/evolution loop
while(generations_passed<max_generations):
    print(f"start generation {generations_passed}")

    #tournament selection
    if do_tournament_selection:
      winners=tournament_selection(tournament_size,population)
      #assigning the winners to be the population
      population=winners
      population=sorted(population, key=lambda person: person['fitness'])

    
    #cross-over winners
    
    #crossing over the winners and producing childeren/kids
    children=cross_over(population, num_original_population, num_lecturers, num_students, student_preferences)

    #checking if the crossed over allocation has all students and no duplicate students.
    valid_after_crossover=quality_check(population)
    
    # add their kids back into population  
    for child in children:
        population.append(child)


    # mutate population
    if(generations_since_big_mutation>5):
        population = mutate_population(population,tenth_percentage_chance,student_preferences)
    # temp=quality_check(population)

    average_fitness_list.append(update_fitness_population(population,student_preferences))
    population = sorted(population, key=lambda allocation: allocation['fitness'])
    best_fitness_list.append(population[0]['fitness'])
    # temp=quality_check(population)


    ##increase generations_passed
    generations_passed+=1

    #calculating and printing out the average preference obtained by a student in each generation.
    average_preference_per_mapping=0
    for allocation in population:
        average_preference_per_mapping+=get_average_allocation(allocation,student_preferences)

    average_preference_in_generation=1+ (average_preference_per_mapping/len(population))
    print("In generation "+str(generations_passed)+" the average preference students get is: "+ str(average_preference_in_generation ) )
    
    generations_since_big_mutation+=1
    do_tournament_selection = True
    #### big mutation if converging at local maxima ####
    len_avgs = len(average_fitness_list)
    curr_avg = average_fitness_list[-1]
    #### this was for avg population ####
    # small_deviation = curr_avg/20
    # if len(average_fitness_list)>5 and generations_since_big_mutation>10:
    #     if(curr_avg-small_deviation < average_fitness_list[len_avgs-5] < curr_avg+small_deviation):

    #### using best_fitness ####
    if len(best_fitness_list)>5 and generations_since_big_mutation>20:
        if(best_fitness_list[-5] == best_fitness_list[-1]):
            population_copy = deepcopy(population)
            best_20_percent = population_copy[0:int(num_original_population*.20)]
            mutated_remainder = mutate_population(population_copy[int(num_original_population*.20):int(num_original_population/2)],700,student_preferences)
            best_20_percent.extend(mutated_remainder)
            population = best_20_percent
            do_tournament_selection = False
            generations_since_big_mutation = 0


    #if perfect fitness then break or max_generations reached break
    if(best_fitness_list[-1]==0): #if convergence has been reached, break out of the loop
        print(f"Converged!")
        break

#sorting by fitness to get the best mapping
population = sorted(population, key=lambda allocation: allocation['fitness'])
print(f"generations_passed={generations_passed}\nbest_dna={population[0]['fitness']}")
print("\n\n  ----------best identified mapping:----------------\n",population[0])

preferences_total=0
students_with_first_pref=0

#printing out the best mapping 
for i in range(0,len(population[0])-1): #loop through keys: lecturer0, lecturer1, lecturer2, ...... lecturer21
    print("------\n")
    print("Iterating through Lecturer: "+str(i+1))
    students_allocated=population[0]["lecturer"+str(i)]["students"] #get students assigned to each lecturer:

    #just to display student 0 as student 1,  student 1 as student 2, student 45 as student 46 etc.
    students_allocated_presentation=[x+1 for x in students_allocated]
    print("Lecturer "+str(i+1)+" was allocated the following students: ",students_allocated_presentation)
    for student in students_allocated:
        lecturer_ranking=student_preferences[student].index(i)
        preferences_total+=lecturer_ranking+1 # the +1 is to convert lecturer 0 to lecturer 1 and so on. min fitness would be 46
        
        #keeping track of student's that got their first preference
        if(lecturer_ranking+1==1):
            students_with_first_pref+=1
        #so this student's preferences are from lecturer 1 to 22 instead of from 0 to 21.
        student_preferences_presentation= [x+1 for x in student_preferences[student]]

        print("Student "+str(student+1)+"'s preferences: ",student_preferences_presentation)
        print("Student "+str(student+1) +" was assigned lecturer"+str(i+1)+" who was their  "+ str((lecturer_ranking+1)) +" preference")

print(f"-----------\n\nStudents, on average got assigned their {preferences_total/num_students}th preference in the best mapping. and {students_with_first_pref} students got their first choice.")
generate_graph(average_fitness_list,len(average_fitness_list), "Plotting average fitness of population against Generations passed","Generations Passed", "Average Fitness of Population", "average")
generate_graph(best_fitness_list,len(average_fitness_list), "Plotting best fitness of population against Generations passed", "Generations Passed", "Best Fitness of Population", "")


