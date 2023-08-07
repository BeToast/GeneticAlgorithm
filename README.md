🏓*Srinivas Ilancheran* and *Blake Preston* 🏓
# 👩🏽‍🎓👨🏼‍🎓👩🏻‍🎓 🔀 🧑🏻‍🏫  
## Genetic Algorithm for allocating students to supervisors for projects

### Representation of allocations
![Representation](https://github.com/BeToast/GeneticAlgorithm/blob/main/img/representation.webp?raw=true)  
*print() of an array of populations*
  
![Representation](https://github.com/BeToast/GeneticAlgorithm/blob/main/img/singlePopulation.webp?raw=true)  
*print() of a single population*
  
We decided to represent the population as a list of “allocations”, with a population size of 100 leading to 100 different pseudorandom “allocations” or mappings between lecturers and students being made randomly. Each index in the population list c­ontains a dictionary that represents a mapping between the 46 students and the 22 lecturers. The aforementioned dictionary contains key-value pairs, with the keys being lecturers and values being dictionaries that contain the lecturer’s capacity and a list of students that have been allocated to them.

The student preferences are represented using a list of lists, with each index containing a list that represents a student’s preferences (index 5 of the student preferences list contains a list that represents student 5’s lecturer preferences)  
  
### Fitness Function 💪🏻
We decided to use an inverted approach to defining the fitness function, ie the mapping with lower fitness would be considered more suitable. The fitness function itself accepts a mapping and a list of student preferences (for lecturers). It then iterates through every lecturer in the mapping, gets the list of students assigned for each lecturer, and sums the index of the lecturer in each of the assigned student’s list of lecturer preferences. With this fitness function, the ideal mapping would have a fitness of 0 (every student gets their first preference (stored in the 0th index of the student’s preferences list).

### Tournament Selection 🏆
The tournament_selection function takes in an integer that represents the tournament_size(whether the fights have 2 participants, or 3 participants or n participants) and the population of mappings. It then ensures that all mappings in the population end up in a fight, by randomly sampling mappings from the population, getting them to fight using the fight() function(which returns the most suitable mapping, in terms of fitness), storing the winner of the fights in a list and then removing the fighters from the population (the population is then set to be the list of winning mappings).

### Mutation 🧬
We decided to implement a directed mutation, where the mutation would have a decent chance at making the fitness of a mapping better(lower). The mutation function takes in the entire population, a variable that represents the chance for mutation to happen and the list of student preferences as parameters. The following process is then applied:  
* For every mapping in the population:
  * For every lecturer in a mapping:
    * If mutation chance is successful:
      1. Obtain the list of students assigned to the lecturer
      2. Identify the most unhappy student (lecturer is farthest down their preferences list, when compared to the other assigned students)
      3. Randomly choose another lecturer in the mapping.
      4. Randomly swap a student assigned to the chosen lecturer with the unhappy student of the current lecturer being mutated.
     
### Cross-over 🔀
Cross-over proved to be one of the more challenging aspects of the assignment to implement. In a broad sense, this would involve lecturers from a section of a mapping being concatenated with lecturers from another section of another mapping (lecturers 1-10 from mapping A would be concatenated with lecturers 11-22 of mapping B, and lecturers 11-22 of mapping A would be concatenated with lecturers 1-10 of mapping B for example).
  
Our cross-over function involved the use of a wrapper function- cross_over() which takes in the population, population size, number of lecturers, number of students and the list of student preferences as parameters. In order to keep the population stable (population size is maintained at original size, even after pruning losers of tournament selection)  cross-over is performed until the number of new mappings generated is enough to fill the void left by eliminated allocations. Pairs of mappings in the population are taken and are passed to a function- cross_over_two_parents() which actually performs the cross-over and returns new mappings. These new mappings are added to a list and the entire list is returned to be added to the population once the satisfactory number of new mappings have been generated via cross_over.
  
The cross_over_two_parents function takes in the 2 mappings that represent parents, the list of student preferences and the number of students and lecturers. It then selects a random number,  bounded by the number of lecturers, which is then used as a “pivot point” to divide the lecturers. Cross-over between the 2 mappings is then performed by concatenating alternating sections of the mappings (lectures are crossed over between mappings).
  
As our primary keys/reference points in the mappings were lecturers, we faced the possibility of students being duplicated or removed when lecturers belonging to different mappings were crossed over with each other. This possibility was almost guaranteed to occur due to the randomness involved in the crossover, and as a result we had to develop helper functions- conflict_resolution() and quality check() to ensure that the mappings in the population were valid (all students were assigned to a lecturer and no student was assigned to more than one lecturer).

#### Cross-over conflict_resolution()
is a function that takes in a newly generated mapping (as a result of cross-over), the list of lecturers and student preferences and the number of students as input parameters. It then makes a list of all the students that are found in the provided mapping, and then identifies the students that are missing from this list (this is done by subtracting a set of the students in the mapping from a set that has numbers in the range 0- num_students ). Duplicate students and the lecturers that have them are then identified and a conflict dictionary is made with the student being the key and the value being a list of lecturers that have them.

The duplicate students are then iterated through and the lecturer that they prefer less is assigned a missing student in place of the duplicate student they have been assigned (if student 4 is assigned to lecturers 7 and 10, and student 4 prefers lecturer 7 more, then lecturer 10 is assigned one of the missing students).

## Results! 🥳🎂
![Representation](https://github.com/BeToast/GeneticAlgorithm/blob/main/img/avgFitness.webp?raw=true)
![Representation](https://github.com/BeToast/GeneticAlgorithm/blob/main/img/bestFitness.webp?raw=true)

-------------

hi Srini, this is Blake from the past. This Blake does not exist anymore.  
Yanno, the Blake you know is only in the past. Is this really me? or just your memory of me?

Github Auth is now weird. I'll roll with the extension now and add in my token later. -Srini
