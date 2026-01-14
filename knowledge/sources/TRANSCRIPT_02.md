0:00
Welcome to my talk, Seven Valms in Seven Days, where we're going to be breaking bloatware faster than it's been built.
0:07
To start this, I need to tell you a story of where I'm playing games. It's summer holiday back in South Africa. Uh
0:13
I'm taking some time out uh and playing my favorite game. At the end of that session though, I notice at the bottom
0:19
right ASUS DriverHub is asking me for install a driver update. Little confused
0:26
by this, I click it and a browser opens up. This driverhub.asis.com
0:32
uh is in a browser and it's asking me for more things to install. This is fairly confusing, but I continue with
0:38
the progress. Eventually, a modal pops up asking me to restart now. Now, I've
0:44
already been a little suspicious by this point, but I've been really suspicious right now. How could this be working?
0:50
The installation completed and I need to reboot. Is there some cloud related thing here that I need to consider? I'm
0:57
not really sure yet. So I go back to driverhub and I click that reboot now button. The reboot happens instantly.
1:06
There is no cloud involved. I have an okay internet connection. But the speed at which this happened was fairly confusing. Anyways, my computer comes
1:13
back and I quickly pop open the dev tools and I realize there's a local web server running on my computer with which
1:20
this driverhub website is interacting. It's also the end of my holiday now because I decided I'm going to take this
1:26
journey that I'm going to tell you about right now. So, thank you for coming to my talk. My name is Leon Jacobs. I'm
1:33
from South Africa and I work for a company called Orange Cyber Defense, more specifically in their Sensost team.
1:38
You can find me online. I'm Leon JZ basically everywhere. Uh, and I do like
1:44
research hacking and building stuff. Today, I'm going to tell you the story about hacking bloatware and a whole
1:50
bunch of vulnerabilities that I found. We're going to look at four products which include ASUS driver hub, MSI
1:56
center, Acer control center, and Razer Synapse 4. All of these vans have been
2:01
fixed. So, if you update to the latest versions of this stuff, uh you'll you'll be you'll be fine. At the end of all of
2:08
that, we'll have some sort of conclusion and talk about what all of this means. I need to prefix some of this talk.
2:14
There's going to be a whole bunch of tools that you're going to see like the list on the left and we're going to look at a whole bunch of code snippets. I've
2:20
tried my best to sort of isolate the bits that you need to look at, but keep in mind that it's going to be quite fast-paced. Uh so, so pay attention. The
2:29
first product to look at will be this ASU driver hub and the two CVE that I found in that. When you look at these
2:36
processes, one of the really useful tools you can use is called process explorer. And specific to ASUS
2:41
driverhub, when you look at what uh backs that program, there are two processes. This ADU.exe
2:48
uh and ASUS driverhub.exe. exe and more interestingly adu.exe listens on a TCP
2:53
socket so things can connect to it. Now at this point I'm looking at these things on my uh home PC where I play
2:59
games but I realize if I want to do some research I want to install this in a virtual machine. Thankfully Asus well as
3:06
to no one's surprise when you install ASUS driver hub in a VM it goes this is not an ASUS product. It's not wrong. Uh
3:13
so we needed to do a little bit of work to get that going. Opening the installer in something like Binary Ninja, it has
3:18
this really nice feature where you can take some code and patch out a branch. Maybe you want to invert the code flow
3:24
or do something else with it. Uh it's fairly simple. So with the installer, I do exactly that really with the point
3:30
being so I can get a successful installation in my Parallels VM. With that installed, I can finally open
3:36
DriverHub in this VM. And again, the VM is handy. I can snapshot, roll back, do all the kinds of things without it being
3:42
a pain. But when I open it up again, it tells me this is not a Asus product. Confult them, they're right. Uh, but
3:49
when you open Burp and sort of see what the requests look like when you open Asus driverhub, you quickly realize
3:55
there's an initialized call where the local web server responds with this is a supported product or not. Because this
4:02
is Burp, I can very easily change a false to true and suddenly my product is supported in my VM. I didn't get all the
4:09
fancy driver updates. I could install the armory crate, but that was good enough premise for me to start playing
4:14
around with this stuff. I've mentioned this before, there were two interesting processes, and for this part, we're
4:20
focusing specifically on ADU.exe because that's the one that has the TCP socket that it was listening on. Opening up
4:27
ADU.exe and something like binary ninja, you'll see a whole bunch of features that this has. Of course, the web server
4:34
was of interest of me. So when doing doing some string searches, you can find endpoints that look like HTTP endpoints
4:40
that you could call. One of those is this reboot endpoint which is really patient zero. What I was working with
4:47
following the flow in how is the reboot implemented. You'll end up in a code piece that will look something like
4:52
this. Really the interesting part is the call to exit windows which will exit Windows. To visualize what we know so
5:00
far, we can quickly have a look at uh how this would work. Imagine a browser where you're browsing to
5:05
driverhub.asis.com. When that page loads, a JavaScript fetch request is made to a local web server,
5:12
which then a native code makes a wind32 API call to exit Windows and reboots
5:18
your computer. I wanted to create a small testing harness for this. So, I wrote some PowerShell to sort of
5:24
replicate this reboot uh reboot feature. I make a web request that looks something like this. And the first
5:29
response I get was an access denied. Now, one thing is really interesting when you look at these things. They often emit an insane amount of logs.
5:37
Logs are really handy for developers, but they're also handy if you don't really know how the software is structured. In the case of ASUS driver
5:44
hub, exactly the same thing is true. There is a log file with a random name that they use, but it's quite useful in
5:50
telling you what's wrong. In this case, I can see there seems to be some origin related error where the origin that I
5:56
passed along was not allowed. In fact, I didn't pass one. So, I modify my test harness at the origin of
6:02
driverhub.asis.com and I get a new error. And everyone knows when you get a new error, that's a
6:07
sign of progress, which is great. Looking at the logs, I can now see the origin is allowed, but the body is
6:13
empty. Uh, so I clearly need to send some content along to actually invoke this reboot. But keep in mind that
6:20
driverhub.as.com lives in a browser. So we can open the console and inspect the JavaScript that's being used to speak to
6:27
that local web server and get a sense of what parameters might be used. In this case over here you finally between this
6:34
minified mess as you would expect find a post request that gives you an idea of what the structure looks like for that
6:40
web server. If I take that knowledge and update my small test harness, it would look something like this. And I'm
6:46
finally at a place where I can also reboot my computer. Totally unnecessary, but this is a good harness for me to
6:52
play with. Cool. With understanding that, let's move on into the first bug. And it's something that I'm just going
6:58
to call the string contains bug. And to understand the string contains bug, we first need to understand how origin
7:04
header validation is supposed to work. Imagine for a moment two tabs where one
7:09
is driverhub.asis.com and the other is driverhub.notasis.com.
7:14
Both of these tabs, both of these domains serve hypothetically exactly the same content. There's no difference, but
7:21
the domain from which you're using to browse to the content. When the page loads and you might want to invoke the
7:27
reboot feature, a fetch request will be made to the reboot endpoint. After which, as a security mechanism by the
7:33
browser, an origin header gets attached. This is a way for the web server on the other end to kind of know where this
7:39
request came from. and how driverHub implemented this as a security feature when it is not asis.com the request will
7:47
fail is where the access denied um originally comes from now the challenge
7:52
is is while reversing this stuff I often sort of rename symbols and sort of try and figure out if I have a rough idea of
7:58
what a function does I'll give it a name with a question mark and in this scenario here I think the function I
8:04
found here was a string contains function question mark was I think uh but I noticed an invocation that
8:10
included this.asis.com argument. Diving into string contains, you can see there's a me compare call that has an
8:17
iterator to sort of compare this the input arguments over uh what the iterator is. To visualize this, it can
8:24
look something like this. Imagine you're going to driverhub.asis.com and it wants to know if this is the
8:30
asis.com origin where you're at. Using the iterator, it will check the string for nine bytes exactly until it goes,
8:36
okay, this looks like asus.com is where this origin came from. However, because
8:41
this is a string contains, if you pass something like driverhub.asis.com, the same effect will occur except it
8:48
will actually stop the moment.asis.com is met. Meaning any origin really can be
8:53
used uh for you to make a request. So that's okay. take my test harness and
9:00
you see that I can do exactly the kind of reboot with the wrong origin. Now, you may have come to this talk for a
9:05
vulnerability, but I'm really just showing you how to reboot your friend's computer. But no, more importantly, you
9:11
can now use an arbitrary origin as long as it contains.com and interact with this local web server
9:17
that driverhub gives you. Now, rebooting is fun, but what's more interesting is gaining r. You might remember from a
9:25
previous uh uh slide that there were a whole bunch of endpoints that we could look at. There are many many other ones
9:31
that are interesting here, but one we'll focus on right now is the update app endpoint. Just like reboot, we can find
9:38
the post body that update app wants and it looks something like this. Focus on
9:43
the URL element for a moment and we can try and pass a full URL to an EXE. Sort
9:48
of test what this thing does. Like if I give it a URL, will it will it download? We update our test harness with exactly
9:55
that URL path that we give. Invoke the request. And if we inspect the log files, we see a line that tells us this
10:01
agent URL can't find.asis.com in it. Well, I showed you the string
10:06
contains bug. So, exactly the same vulnerability exists here where you can just give it a URL to any origin as long
10:13
as.asis.com exists and it would download that which is quite handy. The challenge
10:19
though is when you run it, continue looking at our log files, we get a new error. The universal indicator of
10:24
progress tells us that this one is not signed. This executable that we've sent, but the progress here is our uh content
10:31
has downloaded. Of course, the reverse engineering journey continues and we finally have a look at what the the PE
10:38
signature validation looks like. Uh and you see a line like this. Does one of the properties contain ASUS tech
10:44
computer inc? doesn't really check if the search is valid. Thankfully, tooling already exists that lets us clone PE
10:51
signatures from a valid binary to whatever we want. Critically, the signature won't be valid, but the
10:57
properties exist, which ASUS would then be happy with. So, I want to show you a very quick demo of what this would look
11:03
like. Putting these things together and sort of getting remote code execution with one click. What you're going to see
11:10
now on the left hand side is a web browser of your victim. Somehow you've coerced someone to browse to your
11:16
website. A website that has.asis.com in the URL, a subdomain, whatever you have.
11:22
On the right hand side is just a little bit of showing what's happening. We'll tell the log files of adu.exe to see the
11:28
ex the uh the progress of that process. So on the left I'll go sorry on the
11:34
right we start telling the log files. On the left I go to my domain, browse to my fancy website and we pop calc with one
11:41
click. [Applause]
11:48
Uh what's really interesting about this setup though is none of the components of ASUS DriverHub runs in an elevated
11:54
context. They're all normal user processes that run. However, you can imagine most gamers, they're probably an
12:00
admin on their computer, but they have a US a UAC setting where they'll need to at least click accept or deny. It turns
12:07
out if you have a sidebyside assembly manifest or what seems to be known as a
12:13
UAC manifest that you apply to your target payload, this entire process actually bypasses the UAC prompt as
12:19
well. So if you're an admin, this code execution actually turns code execution in an elevated context. Now Windows has
12:26
some uristics to sort of determine and this is uh an installer based thing. Should I run elevated or not? But the
12:33
way to make this deterministic is to actually implement an al sorry attach an XML like this which has this requested
12:39
execution level uh field with this XML at hand. You can run a tool called
12:44
empty.exe which you'll get with Visual Studio. Pass it the manifest and your target executable and it'll look
12:51
something like what you probably have seen before that sort of signature yellow uh blue shield that it has on top
12:57
of it indicating that when you run this it might run in an elevated context. So for exactly the same exploit, if you
13:04
pass along a .exe that you've added this manifest to, that code execution will
13:09
turn into an elevated code execution bypassing UAC.
13:14
Talking about a uh impact for this, when I looked at my motherboard that started all of this, there's this handy I
13:20
wondered where did this come from? You look at the BIOS and there's this line that says you can download and install ASUS driver up automatically. Uh when I
13:28
found these vulnerabilities, I disabled that fairly quickly. Uh but that should give you an idea how some of the software might actually end up on
13:34
people's computers in the first place. Okay, so that's ASUS driver hub. Uh so let's look at a quick summary. It could
13:41
be an alternative way to reboot your friend's computer or a way to execute arbitrary code. Uh it can auto install
13:47
itself based on this BIOS setting. Uh but really it's the sort of misuse of this strange RPC mechanism. How how you
13:54
invoke those HTTP requests is not great. Uh the Chrome working group actually has a spec proposal which should gate access
14:01
to local resources similar to how um webcams and microphones would be gated
14:07
today. So what it really implies is they're proposing that a little pop-up comes up saying hey this website wants
14:13
to speak to something on the local network which sounds like a handy thing. Uh and I think a little bit to no one's
14:18
surprise the disclosure was a little messy. I'll get back to that a little bit later. Now back I'm still in my
14:24
holiday. I'm a little excited. But I found some really cool vulnerabilities. I'm going to tell ASUS about this. Uh,
14:30
and that's nice. I've disabled this stuff so that no one else exploits me. But I did have a moment and wonder what
14:35
are other vendors doing? If this is one not small vendor, what other things can we see? Uh, so I Google around for
14:43
products, companies that do similar things and unfortunately I come across MSI Center next.
14:50
The thing with MSI Center though, once you install it, like in my VM, uh it has this popup, this display that says for
14:58
you to use this, you need to add your local user to the administrators group. It's a little confusing to me cuz all of
15:04
the processes that run in the back end already run in elevated context. So, I'm not sure why my user needs to be admin
15:10
already. But much like ASUS driver hub, it also has a a component that has a
15:16
local TCP socket that listens for connections. The difference though in this case is actually elevated as well
15:23
because this is a TCP socket and I don't really know what it looks like. Uh I open the client and wireshark to see
15:30
what the connection between a client and that elevated service would look like. And you would see some output that looks
15:35
like this. It's a binary protocol that goes in but the bits that come out seem to be JSON. Uh and it's familiar but but
15:43
not entirely. The nice thing though because the MSI center clients is written inn net the reversing of this is
15:50
fairly easy. There's no offiscation or anything like that. So it's a little bit like looking at a source code review uh from that perspective. Anyways when you
15:57
go through this code a little bit four interesting things come out. There's a launch server method that does some housekeeping make sure the port's
16:04
available etc. Then registers two callbacks where code runs when a new connection comes in and code that runs
16:11
when data is read into that connection. But finally and probably the most important part is this data response
16:17
function that takes a structure of the data that came in on the socket and hands it off to other components. And
16:23
we'll talk about that in a bit. One of the ways in which the software knows
16:29
where things should go is these definition sort of static byte structures of features that it supports.
16:34
Here's an example of a reboot and an uninstall function. But many components in this bloatware has different
16:40
definitions uh which you can see an example of here. With those byte structures defined,
16:46
there is this sort of very primitive compare bytes call that sort of figures out based on how all of the features
16:52
that the software supports when does what which block run. Uh and that would look something like this for the for the
16:58
reboot case. A more complete example, you'll actually see two uh distinct things here. One is a plug-in loader,
17:05
which we'll get to in a second. But in this case for reboot, it actually finally does the reboot by running
17:10
shutdown.exe exe uh as an outcome of this thing. So what we're really saying is we just have a TCP connection that we
17:18
can make to this service and send through the bytes for these commands to make it do something. Uh so I did
17:24
exactly that. But when I sent this along, nothing happens. Referring back a
17:29
little to the wireshock output that I was looking at, I realized that I didn't know yet what those first four bytes
17:35
were for. The bits afterwards started looking familiar to commands that are implemented in this bloatware. But the
17:40
first byes I wasn't too sure of. But regardless, at this point, I don't really know what it means yet. You sort of yolo it, add the four bytes to your
17:48
PC. Uh send it on and your computer reboots again. Now, this might be a talk, seven ways to reboot your
17:54
computer, but but no. Uh more importantly, we now have the primitive where we can interact with the privilege
18:00
process from a non-privileged context. Now, before we get into the bugs, I do want to talk a little bit about MSI
18:06
Cent's software architecture because I think that is quite interesting. When MSI Center boots up, it has this idea of
18:12
a component loader. It scans the program files directory for any DL that matches this API star DLL format, tries and
18:20
loads it uh kicking off an initializer that would register that DL as a
18:26
component that contains commands. Practically what it means is you end up with this sort of component command map.
18:33
uh every component has a unique ID and each one of those components implement unique commands and mapping that to the
18:40
TCP protocol it means every TCP frame defines the component it wants to target with those first four bytes and then
18:47
which of those um commands that it wants to run more crucially with the component
18:52
loader and you'll remember this from the plug-in loader earlier there is this um piece of code that gets to this transfer
18:58
command part which tries to find the component that is loaded and sends it off to that plugin. Really just hoping
19:05
that plugin knows what to do with it. Okay, so let's look at the first bug which is a local privilege escalation in
19:11
this MSI center. One of those commands that um that exist within the MSI
19:17
central server component um is called command auto update SDK and you can see
19:22
it accepts two arguments. One is a target program and arguments for it. Now I think you know where this is going.
19:29
More importantly, when that command is invoked, the target you want to run, let's say this an executable on your
19:34
desktop gets copied to C, Windows temp MSI center SDK. Some verification work,
19:40
which we'll talk about in a bit, happens. But eventually this execute task function runs which schedules an
19:45
immediate scheduled task. That's a mouthful to run that executable and any arguments. Uh, and if supervisor is set
19:53
as true, which is the default, it runs a system. The part before that happens though is a code signing check that uh
20:00
actually checks if this thing that I'm trying to run is actually signed by MSI. I don't have an MSI code signing so
20:06
naturally I can't uh pass this check. Uh and the right way to do it is with the winverified trust call which they do in
20:13
native code. Uh so that was a bit of a bummer and it leaves me with the sort of sad holiday vibes that it's also the end
20:19
of the holiday and I don't have a cool vulnerability until I realized hold on I need to reook at this thing. there is
20:25
something to look at. So if we revisit this autocommand SDK or to update SDK
20:30
command uh and break it down, the first step is to copy the target we want to run. So if we take prog.exe, the
20:37
software will copy that to MSI center SDK in the Windows temp directory. It would then do the verification and
20:44
verification is running whenverify trust over that target file that got written
20:49
to the temp file to the Windows temp directory. If the win verify trust passes, the schedule task is executed
20:56
which is really just saying run that MSI center SDK as system. Uh because it's
21:02
fairly quick uh eventually the schedule task will run it. Uh and which again will be a system. But the challenge here
21:08
is the one that got verified and the one that got run isn't bound in any way
21:13
which gives us this opportunity for a race condition that we could exploit. Taking copy target and imagining we run
21:19
it at two exactly same times. Uh, one might be pone.exe, another could be this. I don't know what MSI Toast
21:26
server.exe does, but it was useful because it had a valid signature. Uh, if we run both of those at the same time
21:32
and it copies it to the same directory, which one of these two is the scheduled task going to run? Uh, and if we do it
21:38
really quickly, there's an opportunity to run the wrong one. So, my exploit plan here is to race to execute with two
21:44
threads. One for this legitimate MSI Toast server thing. Did nothing, but it
21:49
was handy for its search. And the second is then for my payload which I was using to just add users to the local local
21:55
system. Uh the end means that that schedule task would be confused about which one to run because there's no
22:01
binding to who got verified here. So if we take a look at a quick demo of what this privilege escalation might look
22:07
like, it would be something like this. Uh at the back is MSI center server running. Uh just to show the context. Uh
22:14
I start by checking that I don't have an MSI user and I try and add it. That's really just to indicate that I don't
22:20
have access to do that right now. I then run my PC which takes an executable
22:25
which is not signed uh and adds a user. Once the race is won, I can double check
22:30
and I now have a new user which is also a administrator added to the local box.
22:37
[Applause]
22:43
That's a very complicated exploit though uh because LP2 is significantly simpler.
22:49
Uh continuing this process of learning of which commands exist. There's one that lives in APIs support the DL also
22:55
has an execute task routine but the difference here is it was its own implementation of execute task. It
23:01
matches the function prototype but none of the security features that existed in this common lib. And you can see
23:07
probably the developers wanted to get everyone to use the same library but someone decided not to or there's some
23:12
legacy code I don't know. But what is nice about this reimplementation is there's literally zero verification. You
23:19
pass the target, it schedules the task and it runs. So my exploit now becomes
23:24
sort of four lines. I give it the task and you know we get local privilege escalation. It's fairly silly.
23:31
Okay. So in summary for the MSI center, I don't have a um there's another way to
23:36
reboot a computer if that's what you're into, but more importantly, code execution in a privileged context. Comes
23:42
pre-installed when you buy a laptop uh for many of these laptops. Uh but it's yet another example of this sort of RPC
23:48
mechanism that gets misused or is not well implemented. Uh it's a bit of a depressing outcome,
23:55
but I sort of continue, you know, sort of day three, day four of my hacking rampage, and Acer control center
24:00
unfortunately comes on my radar. Uh Acer decided to squish two bugs into one CVE,
24:05
but that's fine. Uh so let's take a closer look at that. When you install it, I if I recall, this one doesn't do
24:12
any verification. It's happy to run on my Parallels VM. Uh but when you look under the hood, you'll see that there
24:17
isn't really a TCP service that we can target. Uh but instead, it's a name pipe. However, the one of the services
24:24
or the privileged services, sorry, one of the services is privileged, which makes it an interesting target. If you
24:30
reverse some of the stuff, you sort of get an idea on how the software is put together. You'll see there's really two
24:35
components, which is very classic client server architecture. There's this native binary running as a service in an
24:41
elevated context, and then there's this normal user client that you would run, but that's written in .NET. And you can
24:48
already see which one of those two would be easier to reverse because a name pipe exists. That's sort of the mechanism of
24:54
which these two can connect. Taking a look at the client, one of the functions that you find that's very interesting is
25:00
called send command by name pipe. It takes a pipe a seven a target path and
25:05
113. When you look at this in a bigger picture, when that gets sent over to the
25:10
native binary somewhere and some of the logic over there which you'll reverse, there's eventually a create process as
25:16
user call with exactly that target that you've given it. So it's such a silly like connect to the name pipe pass a
25:23
target run thing that really for the demo I just sort of give you a screenshot over here. Uh the interesting
25:28
part is coming. But what's nice about this is there was some encoding that I could just rip out of the Acer control
25:34
center client implement it in a small net um program. Give it a pass and it
25:40
would run. But the first thing that confused me here though is this service is running in an elevated context and my
25:46
notepad was not like I was only getting low uh code execution as a lower privilege user and I wasn't too sure
25:53
what was going on there yet. Regardless, moving on to the name pipe. I sort of look at the access and I realize it has
25:59
this file all access thing which is something you explicitly need to get wrong. Like you need to go set that.
26:04
This is not the default. Uh which means although it's not a low privilege escalation, uh a local privilege
26:10
escalation, it's actually remote code execution. So I can run Notepad on your friend's computer. So if we take a look
26:16
at a quick demo, let's see what that looks like. On the left hand side, I have an attacker VM. It's not connected
26:22
to any domain or anything interesting. And on the right hand side there's a user running Acer control center. Uh I
26:28
have a quick look at what the IP configures between the two. Uh and when that is done I run my PC which connects
26:34
to the remote end and asks it to spawn to spawn notepad over that name pipe.
26:41
[Applause]
26:48
I like remote code execution, but I don't like not understanding why it wasn't as a a system. And so I still had
26:54
some questions remaining. Why is this system thing happening? What is that 113
27:00
that I've got uh that I'm sending along with the argument and if assuming 7 is a command? What other commands exist?
27:07
Continuing looking at the server side elevated binary, uh eventually you find
27:12
the other commands that exist there. Uh it had this weird pointer matching thing to invoke them. But regardless, uh
27:18
they'll look something like this. Uh none of the functions that I could see in the Acer control center client would
27:24
invoke any of these other functions. So I sort of left to a place where I needed to manually build my client invoke
27:31
command 6543 uh and get a sense of what the arguments would look like and how they would get
27:36
invoked. To use that I use my favorite tool called Freda which I really like just to get a sense at runtime what does
27:43
the invocation look like and which code parts finally trigger that. The unfortunate thing sadly on comes along
27:50
none of those code parts seem to be doing anything interesting. In fact, it was just a bunch of registry read and writes, etc. So, I revisit that run
27:58
command function where I have a path and I have this 113 that comes in. Uh, I'm a
28:04
few days into this reversing process and I sort of realizing the fatigue sinks in, but thankfully I had a closer look.
28:10
One section of this function has a specific condition for that argument that takes 113. In fact, when you make
28:17
it 114, in fact, incremented by one, you might notice that X300 matches a
28:23
constant when you look at the Windows SDK to have a SID initialize for a higher integrity process. Uh, so when
28:31
this initialize SID function finishes, a token gets built and that gets used to run the target process.
28:37
What that really means is when you have 113, it runs as a normal user. when you make it 114, it doesn't it'll run in an
28:45
elevated context. So change send command by use uh by name pipe making 113 114
28:52
and you now have a elevated command execute or an LP on that system. The
28:58
really neat thing because of the broken named PI permissions, this will work remotely as well.
29:06
Okay, so in summary for the ASA control center, while I don't have another reboot PC for you, you have the ability
29:12
to execute code in an elevated context on the other end. This is also pre-installed on a whole bunch of
29:18
laptops. Uh, and while you know it's not a TCP service, uh, it's sort of the same thing when the name pipe is configured
29:24
like that. Uh, so you definitely want to avoid that if you're doing that stuff.
29:29
Okay, the last target that I want to talk about is is Razer Synapse 4, which uh which also has the CVE. When you
29:36
install Razer Synapse, it's their newer their newer version of their product. Three has been out for a while, but this
29:42
one is not too not too old yet. Uh it'll look something like this when you're installed. I don't own any Razer
29:47
products, so the menus and things are empty, but that's fine. For one moment though, when you look at what's
29:53
happening under the hood, you need to appreciate the amount of processes that's running here for when you
29:58
probably want to change the RGB on your on your product. I don't think it's necessary for that much, but uh this is
30:05
not my domain. Regardless, the keen idea may have already noticed the the process
30:10
that's got the name and what's about to happen, the Razer Elevation Service. Uh it runs a system um and this is an
30:18
interesting target. The challenge with it though is it doesn't unlike the previous targets. There's no listening
30:24
ports or name pipes or anything like that. It's written in C++ which makes the reversing a little bit more
30:30
challenging. Uh and so this target seemed a little hard at first. Attached Promon to it and I interact with it
30:36
using that Electron client. Uh eventually I could get an interaction with the Razer Elevation Service when I
30:43
installed another component. this Razer Chroma thing. I don't know what that is, but the installation triggered the code
30:49
pass. Uh, and it's at this point I realized I needed to reverse that client to see how exactly this code execution
30:56
works. Because it's an Electron app, the sources will be bundled in what's called an SAR archive. And the no team kindly
31:03
maintains a tool that lets you extract these, which really just mean you can end up with the JavaScript source code
31:08
of that Electron application when you run this tool. I like reading source code to find vulnerabilities. So this is
31:15
incredibly handy. When you dig into the detail, you'll find that they're doing what's called a foreign function
31:21
interface using this node FFI library. In fact, it looks like a private fork of a public tool that they're using here.
31:27
So you can see the changes that they have made. But to understand how this works, what really happens is in the
31:33
JavaScript node world, you can call a function like simple service initialize here. And the node FFI library takes
31:40
care of all the translation and loading of native code to make the same function call. It's a very nice obstruction
31:46
layer. It also supports multiplatform, multiarchchitecture. So node FFI will take care of is it x86, is it Mac,
31:53
whatever you running for uh and just call that native code in the end. What this looks like in the Razer Synapse app
31:59
is you'll have a definition client side which when I looked at this the first time I thought this was Freda. the first
32:05
time I'm seeing Freda use non non-reversing case. Uh but it's really a simple definition of what those function
32:11
calls would look like in the native world. To double check that, you open this simple service DL that they're
32:17
using in binary ninja or your favorite reversing tool. Look at the exports and you can clearly see the matching between
32:23
the two. So using this foreign function interface, they're calling a DL natively as the first translation step. I of
32:31
course wanted to play with this. So I came up with a small testing plan. this simple service DL and that's literally
32:36
what it's called in this product uh as a DL I wanted to load and run some functions on it myself and I'd use this
32:44
reverse JavaScript client the electron client to sort of get an idea of what the call flows would be what the
32:49
arguments would be etc I end up in a PC like extremely minified
32:55
and significantly longer that looks something like this there's a function called simple launch user app process
33:02
takes a few arguments but the first three are interesting Uh and while running this of course using some freed
33:09
the arguments look like uh I realized that there's some paths that I can add. When I initially ran this it didn't work
33:15
and it needed a little bit of uh tweaking to understand how those paths relate to each other. It's a little
33:21
complex but I suspect this is a security feature that they've implemented to try and make sure that code only runs from a
33:26
specific folder. You see, parameter one needs to be a folder relative to this app data path and parameter 2 needs to
33:33
be relative to parameter 1. Anyways, what that really boils down to is if you want to make this call, you can give
33:39
this common as an argument which is a path relative to app data and then assuming your payload lives there, give
33:46
that argument to run. When you run that, the DL would be extremely verbose in
33:51
what it's doing. And one of the lines you might spot there is this one that says this PE file is not trusted. Now I
33:58
haven't been able to have a I don't have a Razer Synapse code signing so I'm a fairly disappointed at this stage until
34:05
I realize but actually the code signing is in that client DLL that I have complete control over. They're doing it
34:12
correctly when verified trust is the way to do this. But I can simply patch that out which is exactly what I did. make a
34:19
copy of simple service DLL patch out the P certificate um validation and rerun
34:25
the PC in this case now while everything works there's no error I also don't have
34:30
a user added which is a fairly confusing thing that was when I realized actually
34:35
I've already had this trick where the sidebyside assembly manifest can get added to an exe and I needed this add
34:41
user PC of mine to run in an elevated context so doing exactly the same trick by having the empty.exe exe attached
34:49
this manifest to my payload, I can get code execution uh the way I wanted it to be. So if we take a quick look at what
34:56
the Razer Synapse privilege escalation would look like, uh it would be something like this. I first just check
35:02
that the task is running that uh Razer elevation service. I then double check that I don't have my Razer user yet and
35:09
I also can't add it. Once that is done, uh, I run the what's
35:15
now called Razer Pone over here, which will load my modified DL with all the security checks patched out. Uh, and if
35:21
you quickly see, there'll be a popup that shows a new user added to this to this machine. And we have LBE on on our
35:28
machine.
35:34
I was building these slides for this talk when I'm talking to a colleague about this bug. uh and he effectively
35:41
made my LP a oneliner. The part that I haven't shown you yet that is actually the interface with Razer Elevation
35:47
Service is a COM object and I'm a few days into my reversing journey and getting a lot of fun but I'm not really
35:53
thinking very straight and actually not being successful with COM interfacing. We have a look at OLE view again and we
35:59
get this prog ID for the Razer elevation service. Uh and my colleague shows me how to do the interaction with com
36:06
objects in PowerShell. The first thing you can do is instantiate a new object using the prog ID that you've
36:12
enumerated. And then you can run get member on that to see which methods exist. You can already see where this is
36:18
going. Uh there's a launch process. You've got an option of two of which you just pass in a path and it would run
36:24
that target for you in an elevated context. So you can ignore all this complicated patching and just use this
36:30
oneliner to get LP and Razer Synapse 4 unpatched.
36:35
Okay. So, so let's wrap up quickly. Uh, I didn't only have success, there were
36:41
definitely some failed attempts. I looked at a few targets which included the HP support exist gigabyte control
36:46
center which has a very interesting architecture and Lenovo Vantage. Just last month, uh, a trades partners
36:53
released a blog post where they also looked at Lenovo Vantage, but I think the researcher had more sleep than me
36:58
and they found some really cool bugs that I encourage you to have a look at. A whole bunch of registry things that I
37:03
didn't know was possible. So, have a look at that. In summary, the vulnerabilities that we've looked at included uh these six
37:10
CVEes. They've all been reported and fixed. Uh and Acer decided to make two bugs. One, which I don't really
37:16
understand, but that's fine. Uh but like I said, they're all fixed. It leads me a little bit to talk about the disclosure
37:22
for a bit. And if you are a vendor, please hear me out. In the case of ASUS,
37:27
I try to disclose these vulnerabilities, but their disclosure page has a W and it's blocking bad payloads. I'm sending
37:34
them bad payloads. Please accept them so that you can have a look at the detail. So it made for a frustrating runaround
37:40
to to get that reported. Uh on a more serious note though, there was a research collision here where another
37:47
researcher 2 months after I reported also reported similar bugs. In fact, the same original origin bypass. Uh but
37:54
instead of telling the researcher this has already been been reported and worked on, they sent us the email with
38:00
exactly the same CBE announcement. Except when you click on the email, the CBE is credited to me, effectively
38:06
stringing this researcher along. I'm really sorry about that, Mr. Brew, but what's interesting, if you look at their
38:12
blog, they have since hacked more ASUS things, which I think is a little bit of a revenge hack and very funny to see. Uh
38:18
on the positive side, MSI responded incredibly fast. Like their communication was clear. they were the first ones to fix their bugs, uh, etc.
38:26
So, that's definitely a win. Uh, from a Razer perspective though, they used the bug bounty program which effectively
38:32
fronted the security team. When I reached out trying to talk to someone to talk about this Defcon talk, the CVE,
38:38
etc., uh, I couldn't believe how many tickets on an internal system ended up in my mailbox as they're sort of pushing
38:44
this around. Who can I talk to? Uh, it unnecessarily delayed the process, I think. And I think the communication
38:50
could be a little bit better there. I want to leave you with this idea of what I'm going to call the pone triad. If you
38:56
find a privileged service that has an RPC mechanism, be it a name pipe, com
39:01
object, TCP, whatever you think you're having, uh check if there's an authentication or a validation issue,
39:07
which there probably is. Uh and you will find a vulnerability. In fact, this could also just be a recipe for free
39:13
CBES. In conclusion, I think products built in 2025 doing silly RPC things like this is
39:19
really unnecessary. In fact, if you need that blo if you think you need that bloatware, think twice. There's probably
39:26
better resources to get that. Uh, and if you want to go CVE hunting, check what you have installed right now. And just
39:32
before you uninstall them, maybe you can get a free bug. For all of these vulnerabilities, there's a bunch of PCs
39:38
that I put on GitHub. If you want to play with them, I think there's some more attack surface in many of these tools. You can get it in this QR code,
39:45
which should be public after this talk. That's what I wanted to show you for bloatware hunting, uh, vulnerability
39:51
hunting. Thank you. [Applause]