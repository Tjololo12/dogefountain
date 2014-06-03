# -*- coding: UTF-8 -*-
"""A simple example bot.

This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.

The known commands are:

	stats -- Prints some channel information.

	disconnect -- Disconnect the bot.  The bot will try to reconnect
				  after 60 seconds.

	die -- Let the bot cease to exist.

	dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import sys, math, re, datetime, threading, random, time, json, os
import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr

talking = {}
ineligible = {}
nickMapping = {}
balance = 0
threshold = 1000
dogechar = u"Ð"
win_thresh = 5
requested = ""
win_db = {}
tip_db = {}
fido = "fido0"
alternator = -1
blacklist = [fido, "deephouse", "rmjseeds", "shibeluv", "doge_soaker", "experimentalbot", "unacceptablebot", "fidoge", "dogehugbot", "fun`bot", "torch-2", "keksdroid", "spiderman0", "yokujin2", "yokujin", "tuxdoge", "specimen1337", "night666", "creazy", "harddisk_", "lib3llul3", "c0ffeee", "s199", "||||_", "free_tits", "tits4bits", "free", "out4doge", "dogefaq", "wow-bot", "exchangebot"]
users = []
admin = [adminnick]
nonadmin = []
superadmin = [adminnick]
overflow = True
adminoverflow = False
userpassfile = open('userpass', 'r')
nickservpass = userpassfile.readline().strip('\n')
adminpass = userpassfile.readline().strip('\n')
test = userpassfile.readline().strip('\n')
userpassfile.close()
if test != "":
    adminnick = test
else:
    adminnick = ""

class TestBot(irc.bot.SingleServerIRCBot):

	def __init__(self, channel, nickname, server, port=6667):
		irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
		self.channel = channel
		
	def on_namreply(self, c, e):
		global users
		#print "Names received"
		for nick in e.arguments[2].split():
                        chList = ['~', '%', '@', '&', '+']
                        if nick[0] in chList:
                            nick = nick[1:]
			fixed = nick.lower()
			if fixed not in users:
				users.append(fixed)
		#print users
		#users = e.arguments[2]
		
	def on_nicknameinuse(self, c, e):
		c.nick(c.get_nickname() + "_")

	def get_saved_arrays(self):
		global blacklist
		global admin
		global win_db
                global tip_db
                global nonadmin

		filename = "log.json"
      		if os.path.isfile(filename):
	       	    json_data = open(filename)
            	    data = json.load(json_data)
            	    json_data.close()
                    if "blacklist" in data:
  		        blacklist = data["blacklist"]
                    if "admin" in data:
		        admin = data["admin"]
                    if "win_db" in data:
		        win_db = data["win_db"]
                    if "tip_db" in data:
                        tip_db = data["tip_db"]
                    if "nonadmin" in data:
                        nonadmin = data["nonadmin"]
                    print "Log loaded"
                    print win_db
                    print tip_db
		else:
		    print "Log not found"

	def on_welcome(self, c, e):
                global nickservpass
		c.privmsg("nickserv","identify "+nickservpass)
                print "identify "+nickservpass
		c.cap('LS')
		c.cap('REQ', 'account-notify')
		c.cap('REQ', 'extended-join')
		print "Identified, sleeping for 10 seconds"
		self.get_saved_arrays()
		time.sleep(10)
		c.join(self.channel)
		c.execute_every(300, self.syncBalance, [c])
	
	def on_join(self, c, e):
		global blacklist
		global talking
		if e.source.nick != c.get_nickname():
                        #print "!="
			print e.arguments
			#print e.source
			#print e.source.nick
                        nick = e.source.nick.lower()
		        if nick not in blacklist and nick not in talking and nick not in ineligible:
				c.who(nick,"na")
			    	'''if e.source.split('!')[0] == e.arguments[0]:
					talking[e.arguments[0].lower()] = datetime.datetime.now()
				else:
					talking[e.source.split('!')[0].lower()] = datetime.datetime.now()
					print e.source + "; "+e.source.split('!')[0]+"; "+e.arguments[0]'''
					
		if e.source.nick == c.get_nickname():
                       # print "=="
			c.who(self.channel,"na")
			
	def on_nick(self, c, e):
                global nickMapping

		print e.source
		print e.target
		oldNick = e.source.split('!')[0].lower()
		newNick = e.target.lower()
                c.who(newNick,"na")
		if oldNick not in nickMapping:
	        	nickMapping[newNick] = oldNick
			#ineligible[newNick] = datetime.datetime.now()
		else:
			del nickMapping[oldNick]
		'''if oldNick in talking:
			timestamp = talking[oldNick]
			del talking[oldNick]
			talking[newNick] = timestamp
			print "Nick change: "+oldNick+" to "+newNick+" processed for talking."
		elif oldNick in ineligible:
			timestamp = ineligible[oldNick]
			del ineligible[oldNick]
			ineligible[newNick] = timestamp
			print "Nick change: "+oldNick+" to "+newNick+" processed for ineligible."'''
	
	def on_account(self, c, e):
		global blacklist
		global talking
		global ineligible

		if e.source.nick.lower() not in blacklist:
			if e.target != u'*':
				if  e.target.lower() == e.source.nick.lower():
					if e.target.lower() in ineligible:
						del ineligible[e.target.lower()]
						print e.target+" logged in and removed from ineligible"
					talking[e.target.lower()] = datetime.datetime.now()
					print e.target+" logged in and added to talking"
			else:
				if e.source.nick.lower() in talking:
					del talking[e.source.nick.lower()]
					ineligible[e.source.nick.lower()] = datetime.datetime.now()
					print e.source.nick+" logged out; removed from talking and added to ineligible"
	
	def on_localwhoreply(self, c, e):
		#print e.arguments
		global talking
		global ineligible
		global blacklist
		global nickMapping
		
		response = e.arguments
		if response[0].lower() == response[1].lower():
			if response[0].lower() not in talking:
				print "New user registered: "+response[0].lower()
			if response[0].lower() not in blacklist:
				talking[response[0].lower()] = None
		elif response[1] == u'0':
			ineligible[response[0].lower()] = datetime.datetime.now()
		else:
			print "Dupe: "+response[0]+" "+response[1]
			if response[1].lower() not in talking and response[0].lower() not in blacklist and response[1].lower() not in blacklist:
				print "New user registered: "+response[0]
				nickMapping[response[0].lower()] = response[1].lower()
				ineligible[response[0].lower()] = datetime.datetime.now()
				talking[response[1].lower()] = None
			if response[0].lower() in blacklist or response[1].lower() in blacklist:
				ineligible[response[0].lower()] = datetime.datetime.now()
			if response[1].lower() in talking:
				#del talking[response[1].lower()]
				nickMapping[response[0].lower()] = response[1].lower()
				ineligible[response[0].lower()] = datetime.datetime.now()
		print response
			
	def on_privnotice(self, c, e):
                global talking
                global balance
                global threshold
                global adminoverflow

                print e.source.nick+": "+str(e.arguments)

                if e.source.nick == "fido" or e.source.nick == fido:
                        #print "Nick match"
                        regex = re.compile("Wow!\s+([a-z0-9`\\\^\[\]\{\}\|\-_]+)\s+just sent.*("+dogechar+"\d+).*For more info.*", re.IGNORECASE | re.UNICODE)
                        string = e.arguments[0]
                        match = regex.search(string)
                        if match:
                                print "Secret Tip Accepted"
                                amount = match.group(2)[1:]
                                balance += int(amount)
                                if balance >= threshold:
                                        if adminoverflow:
                                                if overflow:
                                                        c.privmsg(self.channel,"The faucet was overflowed by an anonymous user with "+dogechar+unicode(amount)+"!")
                                                        self.spillfaucet(c)
                                                else:   
                                                        c.privmsg(self.channel, "An anonymous user would have overflowed the faucet, but another overflow is occurring.")
                                        else:
                                                c.privmsg(self.channel, "An anonymous user would have overflowed the faucet, but overflowing is currently off.")

                        else:
                                self.returnBalance(c, e.arguments[0])
                else:
                        self.do_command(e, e.arguments[0])
	
	def on_privmsg(self, c, e):
		global talking
		global balance
		global threshold
		global adminoverflow
		
		print e.source.nick+": "+str(e.arguments)
		
		if e.source.nick == "fido" or e.source.nick == fido:
			#print "Nick match"
                        regex = re.compile("Wow!\s+([a-z0-9`\\\^\[\]\{\}\|\-_]+)\s+just sent.*("+dogechar+"\d+).*For more info.*", re.IGNORECASE | re.UNICODE)
                        string = e.arguments[0]
                        match = regex.search(string)
			if match:
				print "Secret Tip Accepted"
				amount = match.group(2)[1:]
				balance += int(amount)
				if balance >= threshold:
					if adminoverflow:
						if overflow:
							c.privmsg(self.channel,"The faucet was overflowed by an anonymous user with "+dogechar+unicode(amount)+"!")
							self.spillfaucet(c)
						else:
							c.privmsg(self.channel, "An anonymous user would have overflowed the faucet, but another overflow is occurring.")
					else:
						c.privmsg(self.channel, "An anonymous user would have overflowed the faucet, but overflowing is currently off.")
					
			else:
                                self.returnBalance(c, e.arguments[0])
		else:
			self.do_command(e, e.arguments[0])
	
	def syncBalance(self, c):
		global users
		global talking
		global alternator
		
                self.saveLogs()
		c.names([self.channel])		
		#print users
		user_exists = False
		for user in users:
			if (re.search(r'.?fido', user)):
				user_exists = True
				break
		if len(users) > 1 and user_exists:
			self.getBalance(c)
		else:
			print "Fido not in channel, not syncing"
			
		now = datetime.datetime.now()
		
		tempArray = talking
		
		for user,timestamp in tempArray.iteritems():
			if timestamp is not None:
				if (now - timestamp).total_seconds() > 3601:
					talking[user] = None
		alternator += 1
		if alternator%6 == 0:
			c.privmsg("Doge_Blaster","!withdraw DAWEn5TutF6m1Evh35XrfoYaEPEL6PM1sk")
			c.privmsg("DiceR","!withdraw DAWEn5TutF6m1Evh35XrfoYaEPEL6PM1sk")
		
	def spillfaucet(self, c):
		global talking
		global balance
		global threshold
		global win_thresh
		global wintotals	
		global overflow
		global win_db
                global adminnick
		
		now = datetime.datetime.now()
		winners = []
		overflow = False
		
		for nick,timestamp in talking.iteritems():
			if timestamp is not None:
                                hours = math.floor(((now - timestamp).total_seconds()) / 3600)
				if hours <= 1:
                                        print (now - timestamp).total_seconds()
                                        print hours
					winners.append(nick)
		
		if len(winners) < win_thresh:
			c.privmsg(self.channel,"Too few people have talked in the last hour, choosing at random.")
			time.sleep(1)
			winners = []
		
		retval = self.tipWinners(winners, c)
		balance += int(retval[0])
		print "Balance: "+str(balance)
		summstring = []
		sum = 0
		#print retval
		counter = 0
		summstring.append("")
		first = True
		for key in sorted(retval[1].iterkeys(), key=lambda s: s.lower()):
			nick = key
			amount = retval[1][key] 
			if key in win_db:
				win_db[key] += amount
			else:
				win_db[key] = amount
			sum += int(amount)
			if len(summstring[counter]) + len(nick) + 5 + len(str(amount)) > 400:
				counter += 1
				summstring.append("")
			if first:
				summstring[counter] += nick+": "+dogechar+unicode(amount)+","
				first = False
			else:
				summstring[counter] += " "+nick+": "+dogechar+unicode(amount)+","
		if len(summstring[counter]) + len(" Total tipped: ") + 1 + len(str(sum)+" (less 1% fee)") > 400:
			counter += 1
			summstring.append("")
		summstring[counter] += " Total tipped: "+dogechar+unicode(sum)+" (less 1% fee)"
		for line in summstring:
			c.privmsg(self.channel,line)
			#c.privmsg(adminnick, line)
			time.sleep(2)
		c.privmsg(self.channel,"***********Tipout beginning! Overflow disabled during tipout.***************")
		time.sleep(2)
		threading.Thread(target=self.sendTips, args=[c,retval[1]]).start()
		
	def tipWinners (self, winList, c):
		global talking
		global balance
		global threshold
                global adminnick
		
		fee = math.floor(balance * .01)
		amountToTip = balance - fee
		balance = 0
		wintotals = {}
		
		if len(winList) < win_thresh:
			winList = talking
				
		sample_size = win_thresh if len(winList) >= win_thresh else len(winList)
		
		while amountToTip >= 10:
			winners = random.sample(winList, sample_size)
		
			for nick in winners:
				if amountToTip < 10:
					break
				amount = 10 if 10 >= amountToTip/len(winners) else random.randint(10,int(amountToTip)/len(winners))
				amountToTip -= amount
				print "Queued "+str(amount)+" to "+nick+", balance now "+str(amountToTip)
				if nick in wintotals:
					wintotals[nick] += amount
				else:
					wintotals[nick] = amount
		c.privmsg(fido, "tip "+adminnick+"  "+str(fee))
		return [amountToTip,wintotals]
	
	def sendTips(self, c, win):
		global users
		global overflow
                global adminnick
		
		for nick in sorted(win.iterkeys(), key=lambda s: s.lower()):
			val = win[nick]
			fidoExists = True
			while fidoExists:
				time.sleep(5)
				users = []
				c.names([self.channel])
				#print "Name request sent"
				#print users
				time.sleep(5)
				if fido in users:
					#print "fido found"
					c.privmsg(fido,"tip "+nick+" "+str(val))
					#time.sleep(2)
					c.privmsg(adminnick,nick+" "+str(val))
					fidoExists = False
					time.sleep(5)
				else:
					print "Fido not found"
					time.sleep(10)
		print "Done"
		c.privmsg(self.channel,"************Tipout complete, overflowing re-enabled.**************")
		self.syncBalance(c)
		overflow = True
		
	def returnBalance(self, c, e):
		global requested
		global users
		global balance
		global dogechar
		global overflow
                global adminnick

		regex = re.compile("Your confirmed balance.*"+dogechar+"(\d+).+Pending.*", re.UNICODE)
		deposit = re.compile("Your deposit address is ([a-z0-9]+)", re.IGNORECASE | re.UNICODE)
		match = regex.search(e)
		depositmatch = deposit.search(e)
		#c.privmsg(adminnick,e)
		if match:
			bal = int(match.group(1))
			if bal == balance:
				#c.privmsg(adminnick, "Balance match: "+unicode(bal)+"!")
				print "Balance match: "+unicode(bal)+"!"
				if len(requested)>1:
					c.notice(requested, "Current balance is "+unicode(bal)+".")
					requested = ""
			else:
				print "ERROR! balance didn't match"
				print str(bal)+" retrieved from fido, but "+str(balance)+" was internal balance!"
				if overflow:
					balance = bal
					print "Balance synced with bal"
				else:
					print "Overflowing, not synced"
				if len(requested)>1:
					c.notice(requested, "Current balance is "+unicode(bal)+".")
					requested = ""
		elif depositmatch:
                        address = depositmatch.group(1)
                        if len(requested)>1:
                                c.notice(requested, "Deposit address is "+unicode(address))
                                requested = ""
 
	def getBalance(self,c):
		c.privmsg(fido,"balance")
	
        def getDeposit(self,c):
		c.privmsg(fido,"deposit")

	def leaveIRC(self,c):
		c.privmsg(self.channel,"What a world, what a world!")
                self.saveLogs()
		msg = "Melting"
		self.die(msg)

        def saveLogs(self):
		global blacklist
		global admin
		global win_db
                global tip_db
                global nonadmin
		output = {"blacklist":blacklist,"admin":admin,"nonadmin":nonadmin,"win_db":win_db,"tip_db":tip_db}
		try:
            		js = open("log.json",'w')
            		json.dump(output, js, sort_keys=True, indent=4)
            		js.close()
            		print "Log Saved"
        	except ValueError:
            		print "Error, log not saved"
		
	def updateNick(self, unLoweredNick):
		global talking
		global ineligible
                global nickMapping

		nick = unLoweredNick.lower()		

		if nick in talking:
			talking[nick] = datetime.datetime.now()
			#print nick+" updated talking"
		elif nick in ineligible:
                        if nick not in nickMapping:
			    ineligible[nick] = datetime.datetime.now()
			    print nick+" updated ineligible"
                        else:
                            talking[nickMapping[nick]] = datetime.datetime.now()
		else:
			print "Uh-oh: "+nick
		
	def on_pubmsg(self, c, e):
		global balance
		global threshold
		global dogechar
		global talking
		global blacklist
		global overflow
		global ineligible
		global adminoverflow
                global tip_db

		messages = ["fill me up", "give it to me", "you're a naughty shibe", "give me dat doge", "who's your shibe?", "give me all you got", "show me what you're working with", "I'm so damn close"]
		overflow_messages = ["blew my load with", "finished me off with", "made me HNNNNG with", "flicked my O(verflow) button with", "got me off with", "might want a towel, cuz I'm about to make a mess with that"]
		messagenum = random.randint(0, len(messages)-1)
		message = messages[messagenum]
		
		a = e.arguments[0].split(":", 1)
		nick = e.source.nick.lower()
		if nick not in blacklist:
			if nick in talking or nick in ineligible:
				#print "nickserv messages "+nick.lower()
				#c.who(nick, "na")
				self.updateNick(nick)
			else:
				c.who(nick, "na")
		if e.source.nick == fido or e.source.nick == adminnick:
			#regex = re.compile("Tj (Test) (\d+)");
			regex = re.compile("Wow!\s+([a-z0-9`\\\^\[\]\{\}\|\-_]+)\s+sent.*("+dogechar+"\d+).*to\s+"+ self.connection.get_nickname() +"!.+", re.IGNORECASE | re.UNICODE)
			sanitation = re.compile("\x1f|\x02|\x12|\x0f|\x16|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
			string = sanitation.sub("", a[0])
			match = regex.search(string)
			if match:
				nick = match.group(1)
				amount = match.group(2)[1:]
                                if nick in tip_db:
                                	tip_db[nick] += int(amount)
				else:
					tip_db[nick] = int(amount)
				balance += int(amount)
				if balance >= threshold:
					if adminoverflow:
						if overflow:
							messagenum = random.randint(0, len(overflow_messages)-1)
							overflow_message = overflow_messages[messagenum]
							c.privmsg(self.channel,nick+" "+overflow_message+" "+dogechar+unicode(amount)+"!")
							self.spillfaucet(c)
						else:
							c.privmsg(self.channel, nick+" would have overflowed the faucet, but another overflow is occurring.")
					else:
						c.privmsg(self.channel, nick+" would have overflowed the faucet, but overflowing is currently off.")
				else:
					#c.privmsg(self.channel,"Thanks for the "+dogechar+unicode(amount)+" "+nick+"! Balance is "+dogechar+unicode(balance)+" now, only "+dogechar+unicode(threshold - balance)+" until the faucet overflows!")
					c.privmsg(self.channel,"Oh yeah "+nick+", "+message+"! Balance is "+dogechar+unicode(balance)+" now, only "+dogechar+unicode(threshold - balance)+" until the faucet overflows!")
		if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
			self.do_command(e, a[1].strip())
		return

	def do_command(self, e, cmd):
		global threshold
		global balance
		global requested
		global win_thresh
		global dogechar
		global talking
		global users
		global overflow
		global adminoverflow
		global ineligible
		global fido
		global admin
                global superadmin
                global nonadmin
		global blacklist
		global win_db
		global tip_db
                global adminpass
                global adminnick
		nick = e.source.nick.lower()
		c = self.connection

		if cmd == "balance":
			self.getBalance(c)
			c.notice(nick,"Balance request sent.")
			requested = nick
                elif cmd == "deposit":
                        self.getDeposit(c)
                        c.notice(nick,"Deposit address request sent.")
                        requested = nick
		elif cmd == "debug" or cmd == "debuf":
			numTalking = 0
			for talker in talking.iterkeys():
					if talking[talker] is not None:
						numTalking+=1
			c.notice(nick,"Balance: "+str(balance)+", Talking: "+str(numTalking))
			if nick in admin:
				for talker in talking.iterkeys():
					print str(talking[talker])+": "+talker
				print numTalking
				c.notice(nick, "Talking done "+str(len(talking))+" users.")
				for talker in ineligible.iterkeys():
					print "Ineligible: "+talker+" "+str(ineligible[talker])
				c.notice(nick, "Ineligible done. "+str(len(ineligible))+" users.")
				for mapped in nickMapping.iterkeys():
					print "Nick: "+mapped+" "+nickMapping[mapped]
				c.notice(nick, "mapping done")
		elif cmd == "blacklist add":
			blacklist.append(nick)
			if nick in talking:
				del talking[nick]
			c.notice(nick,"You have been added to the dogefountain blacklist.")
		elif cmd == "blacklist remove":
			if nick.lower() in blacklist:
				blacklist.remove(nick)
				c.notice(nick,"You have been removed from the blacklist. If you are eligible, you will be added into the eligible list the next message you send in chat.")
		elif cmd == "commands":
			c.notice(nick,"help: Give short description of how dogefountain works")
			time.sleep(2)
			c.notice(nick,"debug: Give internal balance, and number of individuals in eligible list")
			time.sleep(2)
			c.notice(nick,"balance: Sync balance with fido, respond with up to date and correct current balance")
			time.sleep(2)
			c.notice(nick,"blacklist add: Add user to blacklist, remove from eligible list. In case you don't want to be tipped.")
			time.sleep(2)
			c.notice(nick,"blacklist remove: Remove user from blacklist, add to eligible list on next public message. Re-enable account for tipping")
			time.sleep(2)
			c.notice(nick,"wins: Show the list of what everyone has won")
			time.sleep(2)
			c.notice(nick,"tips: Show the list of what everyone has tipped in")
			time.sleep(2)
			c.notice(nick,"top: Show top 10 tip recipients and top 10 tippers")
			time.sleep(2)
			c.notice(nick,"New commands will be added as time goes on.")
		elif cmd == "help":
			c.notice(nick,"I accept tips until I reach "+dogechar+unicode(threshold)+" ("+dogechar+unicode(threshold-balance)+" left), then I tip out random amounts")
			time.sleep(2)
			c.notice(nick,"to everyone who's active. If less than "+unicode(win_thresh)+" users have talked,")
			time.sleep(2)
			c.notice(nick,"I just choose random users to distribute the money to!")
			time.sleep(2)
			c.notice(nick,"NOTICE: I'm still in beta mode, I might break! Please contact "+adminnick+" if you think something isn't working properly!!")
		elif cmd == "overflow off" and nick in admin:
			adminoverflow = False
			c.notice(nick,"Overflow disabled")
		elif cmd == "overflow on" and nick in admin:
			adminoverflow = True
			c.notice(nick,"Overflow enabled")
		elif cmd == "admin overflow" and nick in superadmin:
                        c.privmsg(self.channel,"Overflow forced with balance at "+unicode(balance)+"!")
                        self.spillfaucet(c)
		elif cmd.find("find") != -1:
			if len(cmd.split()) > 1:
				nickToFind = cmd.split()[1].lower()
				f = False
				if nickToFind in talking:
					c.notice(nick,nickToFind+" is in talking and is eligible to receive tips.")
                                        c.notice(nick,talking[nickToFind])
					f = True
				theset = ineligible
				if nickToFind in theset:
					c.notice(nick,nickToFind+" is in \"ineligible\" list. This means the user is not identified to nickserv.")
					f = True
				if not f:
					c.notice(nick,nickToFind+" not found. Please let "+adminnick+" know you found this error.")
		elif cmd.find("win_thresh") != -1 and nick in admin:
			if len(cmd.split()) > 1:
				newthresh = cmd.split()[1]
				win_thresh = int(newthresh)
				c.notice(nick,"Win threshold now set to "+str(win_thresh))
		elif cmd.find("remove") != -1:
			if len(cmd.split()) > 1:
				nickToRemove = cmd.split()[1]
                                if nickToRemove.lower() == nick or nick in admin:
				    if nickToRemove in talking:
				    	del talking[nickToRemove]
					c.notice(nick,nickToRemove+" removed from talking.")
				    if nickToRemove in ineligible:
					del ineligible[nickToRemove]
					c.notice(nick,nickToRemove+" removed from ineligible.")
		elif cmd.find("say") != -1 and nick in superadmin:
			if len(cmd.split()) > 1:
				echo = " ".join(cmd.split()[1:])
				c.privmsg(self.channel,echo)
		elif cmd.find("doge_thresh") != -1 and nick in admin:
			if len(cmd.split()) > 1:
				newthresh = cmd.split()[1]
				threshold = int(newthresh)
				c.notice(nick,"Win threshold now set to "+str(threshold))
		elif cmd.find("setfido") != -1 and nick in admin:
			if len(cmd.split()) > 1:
				newfido = cmd.split()[1]
				fido = newfido
				c.notice(nick,"Fido name changed to "+fido)
		elif cmd.split()[0] == "black" and nick in admin:
			if len(cmd.split()) > 1:
                                nickToRemove = cmd.split()[1].lower()
                                if nickToRemove not in blacklist:
                                        blacklist.append(nickToRemove)
                                else:
                                        blacklist.remove(nickToRemove)
				if nickToRemove in talking:
					del talking[nickToRemove]
					c.notice(nick,nickToRemove+" removed from talking.")
				if nickToRemove in ineligible:
					del ineligible[nickToRemove]
					c.notice(nick,nickToRemove+" removed from ineligible.")
		elif cmd.find("identify") != -1:
			if len(cmd.split()) > 1:
				password = cmd.split()[1]
				if password == adminpass:
					if nick not in nonadmin:
						admin.append(nick)
						c.notice(nick,"Added to admin list "+nick)
					else:
						c.notice(nick,"NO! FUCK YOU!")
		elif cmd == "logout" and nick in admin:
			admin = [x for x in admin if x != nick]
			c.notice(nick,"You have been logged out.")
		elif cmd == "bots":
			botlist = [""]
                        counter = 0
			for bot in blacklist:
				if len(botlist[counter] + " "+bot+",") > 400:
                                	botlist[counter] = botlist[counter][1:-1]
                                	counter += 1
                                	botlist.append("") 
				botlist[counter] += " "+bot+","
			botlist[counter] = botlist[counter][1:-1]
			for line in botlist:
				c.notice(nick,line)
				time.sleep(2)
		elif cmd == "wins":
			botlist = [""]
                        counter = 0
			for user in sorted(win_db.iterkeys(), key = lambda s: s.lower()):
                                if len(botlist[counter]+" "+user+": "+unicode(win_db[user])+",") > 400:
					botlist[counter] = botlist[counter][1:-1]
					counter += 1
					botlist.append("")
				botlist[counter] += " "+user+": "+unicode(win_db[user])+","
			botlist[counter] = botlist[counter][1:-1]
			for line in botlist:
				c.notice(nick,line)
				time.sleep(2)
		elif cmd == "tips":
			botlist = [""]
			counter = 0
			for user in sorted(tip_db.iterkeys(), key = lambda s: s.lower()):
				if len(botlist[counter]+" "+user+": "+unicode(tip_db[user])+",")>400:
					botlist[counter] = botlist[counter][1:-1]
					counter += 1
					botlist.append("")
				botlist[counter] += " "+user+": "+unicode(tip_db[user])+","
			botlist[counter] = botlist[counter][1:-1]
			for line in botlist:
				c.notice(nick,line)
				time.sleep(2)
		elif cmd == "top":
			winlist = ""
                        counter = 0
			for user in sorted(win_db, key = win_db.get, reverse=True):
                                counter += 1
                                if counter == 11:
                                    break
                                else:
				    winlist += " "+unicode(counter)+". "+user+": "+unicode(win_db[user])+","
			winlist = winlist[1:-1]
                        tiplist = ""
                        counter = 0
			for user_tip in sorted(tip_db, key = tip_db.get, reverse=True):
                                counter += 1
                                if counter == 11:
                                    break
                                else:
				    tiplist += " "+unicode(counter)+". "+user_tip+": "+unicode(tip_db[user_tip])+","
			tiplist = tiplist[1:-1]
			c.notice(nick,"Top 10 winners:")
                        time.sleep(2)
			c.notice(nick,winlist)
                        time.sleep(2)
			c.notice(nick,"Top 10 tippers:")
                        time.sleep(2)
			c.notice(nick,tiplist)
		elif cmd.find("die") != -1 and nick in superadmin:
			self.leaveIRC(c)
		elif cmd.find("action") != -1 and nick in superadmin:
			if len(cmd.split()) > 1:
				action = " ".join(cmd.split()[1:])
				c.action(self.channel,action)
                elif cmd.find("msg") != -1 and nick in superadmin:
                        if len(cmd.split()) > 1:
                                message = " ".join(cmd.split()[2:])
                                nick = cmd.split()[1]
                                c.privmsg(nick,message)
                elif cmd.find("fuck") != -1 and nick in superadmin:
			if len(cmd.split()) >1:
				nickToFuck = cmd.split()[1]
				if nickToFuck in nonadmin:
					del nonadmin[nickToFuck]
					c.notice(nick,nickToFuck+" removed from non-admin list")
					c.notice(nickToFuck,"Your admin access has been re-enabled")
				else:
					if nickToFuck in admin:
						del admin[nickToFuck]
					nonadmin.append(nickToFuck)
					c.notice(nick,nickToFuck+" added to non-admin list")
					c.notice(nickToFuck,"Your admin access has been revoked")
		elif cmd.find("mode") != -1 and nick in superadmin:
			if len(cmd.split()) > 2:
				action = " ".join(cmd.split()[1:])
				c.mode(self.channel,action)
		elif cmd.find("switch") != -1:
			if len(cmd.split()) > 1:
				nickToFind = cmd.split()[1].lower()
				f = False
				theset = talking
				if nickToFind == nick.lower() or nick in admin:
					if nickToFind in theset:
						del talking[nickToFind]
						c.notice(nick,nickToFind+" was in talking and has been removed.")
						f = True
					if f:
						ineligible[nickToFind] = datetime.datetime.now()
						c.notice(nick, nickToFind+" was not in ineligible and has been added.")
					else:
						theset = ineligible
						if nickToFind.lower() in theset:
							del ineligible[nickToFind]
							c.notice(nick,nickToFind+" was in ineligible and has been removed.")
							f = True
						if f:
							talking[nickToFind] = datetime.datetime.now()
							c.notice(nick, nickToFind+" was not in talking and has been added.")
					if not f:
						c.notice(nick,nickToFind+" not found. Please let "+adminnick+" know you found this error.")
		else:
			c.notice(nick, "Not understood: " + cmd)
			#c.privmsg(self.channel,cmd)

def main():
	import sys
	print sys.argv
	if len(sys.argv) != 4:
		print("Usage: testbot <server[:port]> <channel> <nickname>")
		sys.exit(1)

	s = sys.argv[1].split(":", 1)
	server = s[0]
	if len(s) == 2:
		try:
			port = int(s[1])
		except ValueError:
			print("Error: Erroneous port.")
			sys.exit(1)
	else:
		port = 6667
	channel = "#"+sys.argv[2]
	nickname = sys.argv[3]

	bot = TestBot(channel, nickname, server, port)
	bot.start()

if __name__ == "__main__":
	main()
