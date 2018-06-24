from tkinter import *
import csv
import sys
import random
from functools import partial

#CSV file each row follows format: ID,QUESTION,ANSWER A, ANSWER B, ANSWER C, ANSWER D, CORRECT ANSWER, NO. CORRECT, NO.ATTEMPTS, IMAGE

class Question:
	def __init__(self, prompt, options, answer, id_no):
		self.id = id_no
		self.prompt = prompt
		self.options = options
		self.answer = answer
		self.attempts = 0
		self.correct = 0
		self.image = None


#################### Check if button clicked was correct answer or not and update stats ######################
	def check(self, letter, view):
		global answers_correct
		if(str(letter) == str(self.answer)):
		    label = Label(view, text="Correct!")
		    answers_correct += 1
		    self.attempts += 1
		    self.correct += 1
		else:
			self.attempts += 1

			label = Label(view, text="Wrong! The correct answer was " + str(self.answer))
		label.pack()
		if label_photo:
			label_photo.destroy()
		for w in view.winfo_children():    ## added 6th April, disables buttons whilst waiting for next question to prevent double presses
			w["state"] = "disabled"
		view.after(2000, lambda *args: self.unpackView(view))  ## moves on after 2 seconds


################# Add buttons to the window frame #################

	def getView(self, window):
		global label_photo
		view = Frame(window)
		main_label = Label(view, text=self.prompt)
		button_a = Button(view, text=self.options[0], command=lambda *args: self.check("A", view))
		button_b = Button(view, text=self.options[1], command=lambda *args: self.check("B", view))
		button_c = Button(view, text=self.options[2], command=lambda *args: self.check("C", view))
		button_d = Button(view, text=self.options[3], command=lambda *args: self.check("D", view))
		if self.image != None:
			source = self.image
			photo = PhotoImage(file=source)
			label_photo = Label(view, image = photo)
			label_photo.image = photo
			label_photo.pack(side="bottom")
		else:
			label_photo = False
		main_label.pack(side="top")
		button_a.pack(side="top")
		button_b.pack(side="top")
		button_c.pack(side="top")
		button_d.pack(side="top")

		return view

################# Hiding question from frame before displaying the next ######################
	def unpackView(self, view):
		view.pack_forget()
		askQuestion()


############## Reads questions from CSV and puts them into a class object then into a list 'questions'################
with open('questionbank.csv', 'r', encoding='utf-8', errors='ignore') as f:
	question_bank = csv.reader(f)
	questions = []
	for row in question_bank:
		the_options = []
		for i in range(2,6):
			the_options.append(row[i])
		this_question = Question(row[1],the_options, row[6], row[0])  #question, options, answer, id
		if row[9] != 'None':
			this_question.image = row[9]
		questions.append(this_question)


############# Displays summary if all questions answered. Otherwise displays next question. #######################
def askQuestion():

	global questions, window, index, button, correct, number_of_questions, summary
	if(len(questions) == index + 1):
	    summary = Label(window, text="Summary: " + str(answers_correct) + " out of " + str(number_of_questions) + " answered correct")
	    summary.pack()
	    return
	button_restart.pack(side='bottom')
	button_start.pack_forget()
	button_edit.pack_forget()
	index += 1
	questions[index].getView(window).pack()


#######################################################################################################################
def restartQuiz():

	with open('questionbank.csv', 'r', newline = '') as readFile:
		reader = csv.reader(readFile)
		reader = list(reader)
		for question in questions:
			for row in reader:
				if question.id == row[0]:
					row[8] = int(row[8]) + int(question.attempts)
					row[7] = int(row[7]) + int(question.correct)
		with open('questionbank.csv', 'w', newline='') as w:
			writer = csv.writer(w)
			writer.writerows(reader)

	for question in questions:
		question.attempts = 0
		question.correct = 0
	for widget in window.winfo_children():
		widget.destroy()
	mainMenu()


def quitQuiz():
#using ID matching from csv file to self.id, updates attempts correct/attempts answered in csv file
	restartQuiz() #stores stats before quitting
	window.destroy()

#################################################################################################################

def getStatistics(idno):
	with open('questionbank.csv', 'r', newline = '') as readFile:
		reader = csv.reader(readFile)
		reader = list(reader)
		for row in reader:
			if (idno == row[0]) & (row[8] != "0"):
				return(int(row[7])/int(row[8])*100)
			elif (idno == row[0]) & (row[8] == "0"):
				return("No statistics for this question yet")

def editQuestions():
#display questions in GUI with ability to click question to edit. Each question will have stats displayed next to it.
	for widget in window.winfo_children():
		widget.destroy()
	button_back = Button(window, text="Back to menu", command = restartQuiz)
	button_back.pack()
	button_end = Button(window, text="Quit", command=quitQuiz)
	button_end.pack()
	Label(window, text="Click on a question to edit. Percentage correct is shown next to each question").pack()

	for i in range(0, len(questions)): 
		Button(window,text=str(questions[i].prompt) + "        " + str(getStatistics(questions[i].id)) + "%", command = partial(change_or_delete, questions[i])).pack()
	button_add = Button(window, text="Add new question", command= addQuestion)
	button_add.pack()


################## Edit or delete question ################################

def change_or_delete(questionChange):
	for widget in window.winfo_children():
		widget.destroy()
	button_back = Button(window, text="Back to menu", command = restartQuiz)
	button_back.pack()
	button_end = Button(window, text="Quit", command=quitQuiz)
	button_end.pack()
	Label(window, text="You have chosen the following question to edit: ").pack()
	Label(window, text= questionChange.prompt).pack()
	

	def deleteQuestion():
		global questions
		with open('questionbank.csv', 'r', newline = '') as readFile:
			reader = csv.reader(readFile)
			reader = list(reader)
			del reader[int(questionChange.id) - 1]
			with open('questionbank.csv', 'w', newline='') as w:
				writer = csv.writer(w)
				writer.writerows(reader)
		##same as above code to read in questions 
		with open('questionbank.csv', 'r') as f:
			question_bank = csv.reader(f)
			questions = []
			for row in question_bank:
				the_options = []
				for i in range(2,6):
					the_options.append(row[i])
				this_question = Question(row[1],the_options, row[6], row[0])  #question, options, answer, id
				if row[9] != 'None':
					this_question.image = row[9]
				questions.append(this_question)
		editQuestions()

#################### Editing a question #####################################

#CSV file each row follows format: ID,QUESTION,ANSWER A, ANSWER B, ANSWER C, ANSWER D, CORRECT ANSWER, NO. CORRECT, NO.ATTEMPTS, IMAGE
	def Change(arg):
		for widget in window.winfo_children():
			widget.destroy()
		button_back = Button(window, text="Back to menu", command = restartQuiz)
		button_back.grid(row=0,column=0)
		button_end = Button(window, text="Quit", command=quitQuiz)
		button_end.grid(row=0,column=1)
		Label(window, text="Type a new value for this: ").grid(row=1)
		change_value = Entry(window)
		change_value.grid(row=2)

		def submitChange():
			global questions
			with open('questionbank.csv', 'r', newline = '') as readFile:
				reader = csv.reader(readFile)
				reader = list(reader)
				my_id = int(questionChange.id) - 1
				if arg == "qu":
					reader[my_id][1] = str(change_value.get())
				elif arg == "op1":
					reader[my_id][2] = "(A) " + str(change_value.get())
				elif arg == "op2":
					reader[my_id][3] = "(B) " + str(change_value.get())
				elif arg == "op3":
					reader[my_id][4] = "(C) " + str(change_value.get())
				elif arg == "op4":
					reader[my_id][5] = "(D) " + str(change_value.get())
				elif arg == "ans":
					reader[my_id][6] = str(change_value.get())
				elif arg == "img":
					reader[my_id][9] = str(change_value.get())
				with open('questionbank.csv', 'w', newline='') as w:
					writer = csv.writer(w)
					writer.writerows(reader)
			with open('questionbank.csv', 'r') as f: #alters csv file and returns to editing
				question_bank = csv.reader(f)
				questions = []
				for row in question_bank:
					the_options = []
					for i in range(2,6):
						the_options.append(row[i])
					this_question = Question(row[1],the_options, row[6], row[0])  #question, options, answer, id
					if row[9] != 'None':
						this_question.image = row[9]
					questions.append(this_question)
			editQuestions()
		Button(window, text='Submit', command=submitChange).grid(row=3, column=0, sticky=W, pady=4)

	def editaQuestion():
		for widget in window.winfo_children():
			widget.destroy()
		button_back = Button(window, text="Back to menu", command = restartQuiz)
		button_back.grid(row=0,column=0)
		button_end = Button(window, text="Quit", command=quitQuiz)
		button_end.grid(row=0,column=1)
		Label(window,text="Editing question: " + questionChange.prompt).grid(row=1)
		Label(window,text="Choose what to edit: ").grid(row=2)
		button_question = Button(window, text="Question: " + questionChange.prompt,command=partial(Change,"qu")).grid(row=3)
		button_optiona = Button(window, text=questionChange.options[0],command=partial(Change,"op1")).grid(row=4)
		button_optionb = Button(window, text=questionChange.options[1],command=partial(Change,"op2")).grid(row=5)
		button_optionc = Button(window, text=questionChange.options[2],command=partial(Change,"op3")).grid(row=6)
		button_optiond = Button(window, text=questionChange.options[3],command=partial(Change,"op4")).grid(row=7)
		button_correct = Button(window, text="Correct answer: " + questionChange.answer,command=partial(Change,"ans")).grid(row=8)
		button_image = Button(window, text="Image",command=partial(Change,"img")).grid(row=9)

	Button(window, text="Edit", command=editaQuestion).pack()
	Button(window, text="Delete question", command=deleteQuestion).pack()

############################ Adding a new question ###################################################################

def addQuestion():
	for widget in window.winfo_children():
		widget.destroy()
	button_back = Button(window, text="Back to menu", command = restartQuiz)
	button_back.grid(row = 0, column = 0)
	button_end = Button(window, text="Quit", command=quitQuiz)
	button_end.grid(row = 0, column = 1)
	Label(window, text="Question:").grid(row=2)
	Label(window, text="Answer A:").grid(row=3)
	Label(window, text="Answer B:").grid(row=4)
	Label(window, text="Answer C:").grid(row=5)
	Label(window, text="Answer D:").grid(row=6)
	Label(window, text="Correct letter (Enter Capital):").grid(row=7)
	Label(window, text="Image address (If none, enter None):").grid(row=8)
	d2 = Entry(window)
	d3 = Entry(window)
	d4 = Entry(window)
	d5 = Entry(window)
	d6 = Entry(window)
	d7 = Entry(window)
	d8 = Entry(window)
	d2.grid(row=2, column=1)
	d3.grid(row=3, column=1)
	d4.grid(row=4, column=1)
	d5.grid(row=5, column=1)
	d6.grid(row=6, column=1)
	d7.grid(row=7, column=1)
	d8.grid(row=8, column=1)
	def add_new_question():
		with open('questionbank.csv', 'r', newline = '') as readFile:
			reader = csv.reader(readFile)
			reader = list(reader)
			new_id = number_of_questions + 1
			reader.append([new_id,d2.get(),"(A) " + d3.get(),"(B) " + d4.get(),"(C) " + d5.get(),"(D) " + d6.get(),d7.get(),0,0,d8.get()])
			with open('questionbank.csv', 'w', newline='') as w:
				writer = csv.writer(w)
				writer.writerows(reader)

	Button(window, text='Submit', command=add_new_question).grid(row=9, column=1, sticky=W, pady=4)


############################ Detects if user inactive https://stackoverflow.com/questions/38600625/do-something-after-a-period-of-gui-user-inactivity-tkinter ##########

def user_inactive():
	restartQuiz()

timer = None
def resetTimer(event = None):
	global timer
	if timer is not None:
		window.after_cancel(timer)
	timer = window.after(60000, user_inactive)
	window.bind_all('<Any-KeyPress>', resetTimer)
	window.bind_all('<Any-ButtonPress>', resetTimer)



##################### Username password ###################

def checkPermission():
	for widget in window.winfo_children():
		widget.destroy()
	button_back = Button(window, text="Back to menu", command = restartQuiz)
	button_back.grid(row=0)
	def check_entry_fields():
		# print("First Name: %s\nLast Name: %s" % (e1.get(), e2.get()))
		if (e1.get() == "username") & (e2.get() == "password"):
			editQuestions()
		else:
			restartQuiz()

	Label(window, text="First Name").grid(row=1)
	Label(window, text="Last Name").grid(row=2)

	e1 = Entry(window)
	e2 = Entry(window)

	e1.grid(row=1, column=1)
	e2.grid(row=2, column=1)

	Button(window, text='Submit', command=check_entry_fields).grid(row=3, column=1, sticky=W, pady=4)

############## GUI Main menu ####################### changed this to a function so that restart quiz can call it 06/04/2018
window = Tk()
def mainMenu():
	global index, questions, number_of_questions, button_start, button_restart, button_end, button_edit, answers_correct
	random.shuffle(questions)
	index = -1
	answers_correct = 0
	number_of_questions = len(questions)
	button_start = Button(window, text="Start", command=askQuestion)
	button_restart = Button(window, text="Restart", command=restartQuiz)
	button_end = Button(window, text="Quit", command=quitQuiz)
	button_edit = Button(window, text="Edit questions",command=checkPermission)

	button_end.pack(side='bottom')
	button_edit.pack(side='bottom')
	button_start.pack(side='bottom')
mainMenu()
resetTimer()
window.mainloop() #keeps the window on the screen 



#extra features:  
#core features: neaten Tkinter


#done:
#deleting question
#editing questions
#restart button,
#highlighting correct answer
#statistics updated upon quitting
#username/password
#restart after a time
#images
#adding questions
