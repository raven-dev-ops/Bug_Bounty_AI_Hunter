0:00
All right. You may have heard of mainframe pen testing and exploitation
0:05
mainly from our next speaker. I defcon, please give a welcome to the soldier of
0:10
fortree. Wow, that was awesome. The other room
0:17
cheered for me. That was great. Um, morning everybody. I really appreciate youall coming to a Sunday morning talk
0:22
at Defcon. Uh, front row, I'm going to need your help. I can't see anybody else. And if my hand starts to drop and
0:29
you can't hear me anymore, can you guys just be like, "Hey, we got you." Thank you. Thank you. Thank you so much. All right. So, for those who don't know,
0:36
um, my name is Phil Young. I'm the director of We're just waiting for them to calm down. I don't know what's going
0:42
on over there. Um, so I'm the director of mainframe pen testing at Net Spy. You
0:47
might also know me by my other name, Soldier of Forran. I was a mainframe
0:53
hacker, like a '90s hacker kid. I was a mainframe security enthusiast before I
0:59
started doing this professionally. Um, I'm a terrible karaoke singer. Um, and
1:05
just just so folks know, like I always felt like an outsider, especially
1:11
at DevCon, and I still sometimes feel like an outsider. So, if that's if you feel like that, don't. That's everybody
1:17
feels like that. Um, and I've been doing like professional mainframe pen testing for about 10 years. Um, this was
1:25
supposed to be a co- talk, but uh, unfortunately my co-speaker is no longer with us. Um, he had to go home to take
1:33
care of his kid going to college, so he's not here.
1:38
So, but still going to talk about him. So, he was a '90s hacker kid. Uh, he was also a mainframe security enthusiast. He
1:44
loves show tunes. He's really good at reverse engineering things. the best reverse engineer I know, especially when it comes to mainframes. Dude's a
1:51
freaking genius. Uh, he's also been testing mainframes for 10 years. Now, there's a third person in this photo who
1:59
we didn't invite, but he's he's the OG mainframe hacker, and we we wanted to
2:05
make sure we we shine a light on him as well. Before Chad and I came along, he was like the only mainframe hacker who
2:13
was publicly talking about how to do like mainframe pentesting right at mainframe conferences, not places like
2:19
Defcon. I've been trying to get him to come to DevCon for years, but I wanted to make sure we talked about him cuz he is the OG for mainframe hacking now.
2:27
Since Chad and I have been friends for the better part of 10 years, uh, I need
2:32
help with my I'm a great coder, especially when it comes to assembly. And so I will oftent times send my code
2:38
to Chad so that he can help review the code because it doesn't work right. And
2:45
every time I send him a piece of code, he puts me on blast on Twitter first,
2:50
then he fixes it. Speaking of Chad, since Chad couldn't be here, what I did was I told him, "Hey,
2:57
send me like 10 to 15 photos of yourself." Not telling them what they're going to
3:03
be for. And then I said, "Hey, I want you to give me quotes that I will put in
3:09
the talk." Okay, so remember this slide. Look at the bottom where and yes, I did write that. I hope it's enough. Okay.
3:16
And now I when I sent Chad the deck and I said, "Hey, I want you to put inspirational quotes or technical quotes." But I told him, I mistakenly
3:23
told him, "I will read off whatever you put verbatim."
3:28
So the first thing he sends me with respect to this slide is he said it was not enough. So thanks Chad, I appreciate
3:35
you. Um, this is not so bad. I can actually see a bunch more of you than I thought. So we're going to try try this
3:41
out. Who here can tell me where the main frame is in this picture?
3:51
Don't be shy. You can just yell it out. The system. You got to be Someone said
3:57
system in the back. Can you be a little more specific?
4:03
Where the tapes are? No. Yeah. Yeah. This guy put his hand up. Yes.
4:12
The box, the red box in the corner that says 360 on it. Yeah. That's the main frame, right? That is the main frame.
4:18
The reason it's called a main frame is because it holds all the CPUs and memory, right? It is the main frame.
4:25
That's where the work comes from where you host all the CPU, all the all that stuff. The rest of this is just IO,
4:32
right? It's you got your terminal, you've got your card reader, you've got a dude pressing buttons for some reason,
4:38
right? Like the but everything in that that one thing that's the main frame. Now, today in a modern data center, this
4:45
is what the main frame looks like. It's exactly the same. The old Thank you. The only difference is
4:51
this is the main frame. And now this one box, I promise you right now, there is a box exactly like
4:59
this in some bank or some airlines data center and it is processing thousands of
5:04
transactions a minute right now and it's doing it flawlessly and it's it's it's
5:10
the workhorse of the enterprise and lots of enterprises still rely on this
5:15
platforms. You have no idea how many articles come out. Mainframe's dead. Mainframe's going away. Uh, this
5:21
company's moving off the mainframe. This other company's moving off the main frame. There's so many announcements.
5:27
This company's moving off the main frame. There's never announcements. We successfully moved off the main frame.
5:33
Okay, they never do. They start some CIO comes in, starts the process, they got about halfway and that CIO quits, right?
5:38
That's usually the steps. So, but so many companies rely on this platform today, right? You've got airlines rely
5:46
on it. I mean, if you flew on any of the major airlines, a mainframe is processing your transactions. Every time
5:51
you use your credit card or debit card, mainframes are involved in some capacity, right? Auto manufacturers,
5:58
obviously banks, but even companies like UPS use mainframes. If it's older than
6:03
say like it's like a 50-year-old plus company, guaranteed they're using a mainframe. Okay.
6:10
Before we get too far into the talk, I need to talk about some terminology
6:16
that's important for you all. So, you know, rack F is what's called a external
6:22
security manager. So, there's actually three of them. Uh, Rackf, top secret, and ACF2. Now, it's called external
6:30
security manager even though it runs on the main frame as part of the operating system. But think of it like Active
6:36
Directory. if you could replace active directory with something else, right? Better or worse, it's the same concept,
6:43
right? So, the reason is the the operating system itself is doesn't
6:48
really care. It just asks what's called the SAF router and it says, "Hey, is this okay?" And then the router knows
6:53
which product to route it to. You can only run one at a time. But, so that's rackf. Now, rackf controls sort of all
7:00
the security permissions on the mainframe. In rackf there are user attributes
7:06
called special and operations. Special and operations allows you to
7:12
edit any file to change any file to give
7:17
yourself whatever permissions you want in the rack. If you have system special but not operations, you can give
7:23
yourself operations, right? If you have operations but not special, you can
7:29
download the rackf database and crack all the passwords, right? So either or gives you complete control over the
7:35
system. Uh APF libraries are uh imagine if you had a folder where you
7:42
could put uh set UID any program you put in there was automatically like set UID
7:48
right very similar concept but you can get into essentially ring zero so long as you put your binaries in there right
7:54
that is the control that mainframes use. Basically, when you put a program in
7:59
that folder, it is allowed to run in a supervisor state with the CPU. That's
8:05
what it means. That's how they control how programs can run. Key zero is is
8:11
this is all terminology you need to know. Key 0 is the every page of memory
8:16
has a key. Key 0. If your if your process is running in key zero, you can
8:23
edit any location, any page of memory you want. Otherwise, the only other time that works is if your keys match, right?
8:29
So, if I'm in key8 and the memory space is in key 8, then I'm allowed to edit that region of memory. But if not, I
8:35
can't. Now, I we would like to think that, you
8:40
know, these are all myths about mainframes, right? But when it comes to
8:48
these myths, this is a slide that Chad gave a talk on 10 years ago
8:53
and even today we keep hearing about these myths, right? It is crazy.
9:00
Okay, so there's really four main attack paths on the mainframe. You get your
9:06
network attacks, right? Normal network type attacks, right? NMAP works fine. All these things. On top of that though,
9:13
we have SNA networks. So that's that's a completely different type of network that runs. Uh we have the file system,
9:20
right? You'd be surprised sometimes on pentest I go in and I see I have access I have like write access to 30,000 data
9:27
sets uh or read access to like sensitive company information like 110,000 data
9:33
sets. It is it's crazy. Um external security manager that's the other attack path. That's where we go in and we look
9:39
at oh do I have access to this? Do I have access to that? And in fact, some of the things we're going to talk about today are because of misconfigurations
9:46
in the external security manager. And lastly, what this bulk of this talk is about is ZOS Unix. And the reason the
9:54
reason we want to talk we wanted to talk about ZOS Unix was because we really we used to joke that like Unix was the
10:02
gateway drug to mainframe hacking cuz it's so familiar, right? It is such a
10:07
familiar thing to you, especially if you use Linux. In fact, I have a pretty good view of the audience. Can I have a show
10:13
of hands who's familiar with Linux, right? Like most of the audience, right? So that's good because it's very similar
10:21
but also a little bit different, right? So it's based on system V, right? Or
10:27
system 5 and it really didn't get built out until mid90s, right? So so the IBM
10:35
operating system is called ZOS, right? So it runs zos and inside zos you run
10:41
Linux or you run Unix sorry it was developed in 1994 it wasn't really a
10:47
core part of the operating system it was based on like Unix from from 8 from bell
10:53
those kind of things in '96 it obtained pix compliant and it took over running
10:59
TCP IP for zos prior to that it was all jobs and stuff but instead they just built the TCP IP implementation on Unix.
11:08
They rebranded it in '98 to Unix system services uh and it continued to grow a
11:14
little bit more and then today they rebranded it again to Zos Unix. And for
11:20
those curious uh Linux was released in '91. So just a little timeline. Now when
11:26
it comes to Unix again it's like Linux. It's a little bit different. Uh you only
11:32
get two shells. Bin SH which sucks. bin TCSH was sucks a little less, right?
11:38
They're both not great. Uh but that's all we get. It's look, if you everyone here knows
11:44
Linux, I'm not going to explain how file systems work in in PZIX environments. Uh you get file permissions, right? Regular
11:50
file permissions, but here's where it gets a little funky. You can also have other permissions that you put into your
11:57
ESM, right? Like rack f. So you can have say I have read access to this file
12:03
according to the file system but when I try to read it rackf says no that folder is only for admins right uh where that
12:11
gets challenging is sometimes you can mix those up and not do a great job uh you access the Unix environment
12:17
there's a whole bunch of ways to access the Unix environment uh you access it through the command uh in TSO so I'm not
12:25
there's other talks there's whole other talks about hacking in TSO but like you just type OBS and you get like a Unix prompt
12:31
uh SSH sessions, which is what we're going to use for this talk, right? Because we're we'll try to demonstrate
12:36
how you can do all of this in in Unix. Um or you can use JCL, you can use um
12:42
BPX bash, you can use Rex scripts, you can call it from um C programs. There's
12:48
all kinds of things you can do assembly programs, right? I know Chad wrote a module for metas-ploit that spawns a
12:55
Unix shell uh using assembly. So, you can call it all kinds of ways. What's interesting is you can also access data
13:02
sets from within Unix using this super funky command, right? So you do like
13:08
slash then the name of the data set you want to interact with uh and then you pipe it to that's where you're copying
13:15
it to. Only a it's frustrating because only a handful of commands support it and it's not clear. So like I know copy
13:20
works. I know cat works because a client I was on wouldn't let you copy a data set. So I just catted it and piped it
13:27
out like redirected the output. Um, Grep does not support it for some reason. So
13:33
it just sort of like depends on what IBM wanted to do. Now again, if you're familiar with
13:39
Linux, this should all be very familiar, right? Close enough, right? You've got normal
13:46
commands, you've got your normal stuff going on here. You can cat files. Um, the fact that it's posit compliant means
13:54
you can do all the normal things you can do in a Unix environment, right? It's it's not some crazy uh thing going on.
14:03
Okay, so here's the next Chad quote. Um,
14:08
I can see it on my screen here. I don't ask me about Vegas Phil. That's it. So,
14:14
I'm not going to leave time for questions, just so you know. So, don't So, good luck. All right. When we made
14:20
this talk, you know, we wanted it to sort of walk you through step by step
14:25
how we do a pentest, right? Because there's lots of tools and stuff that exists now that we didn't have like 10
14:32
years ago and and it's important to understand how we start cuz like jumping in straight to the end is sucks. So
14:39
there's a whole bunch of tools that exist today. These didn't exist 10 years ago because
14:45
Chad and I wrote them, right? So you have you have a tool called Enum. That's a Rex script. So for those who don't
14:51
know, Rex is a scripting language. If you actually Quick question, who here ever used an Amigga?
14:58
Yeah. Yeah, that's that's way more than I thought. So Amigga came with Rex. Um Rex is a scripting language. It was
15:05
created by IBM as a 10% project. But anyways, Rex runs in Unix um natively.
15:11
And so we write a bunch of our scripts in Rex. We we also have another script
15:16
called OVs Enum and that script um is based on line. I'll get to that script
15:22
in a bit. We also have a couple of Java tools called file traversal and zoshog. Those allow us to sort of map out the
15:29
file system like do we have read access? Are there passwords in them? Um and then we have another tool called port scan
15:35
which we'll talk about when we get to egress. Um all of this is freely available on my GitHub. So if you wanted
15:43
to test them out or play with them, they're freely available, right?
15:49
And if you have a keen eye, you may have saw there was a file called all.jcl.
15:55
Getting getting things onto the main frame during a pentest can be very challenging sometimes.
16:01
Uploading multiple if you have to upload one file, it's a pain. If you have to upload multiple files, it's a bigger pain. Companies for some reason try to
16:08
like limit your ability to upload. There's always a way around it, right? There's always a way around it. So what
16:13
we do is we package everything up, all of those scripts into one JCL and then it just runs by itself. It adds all
16:20
those programs. Now how do we get it to the main frame? We you can just use SCP.
16:27
Problem is SCP only supports binary file transfer.
16:34
And I'm sure as you're reading the slide, you're kind of seeing why. Does anybody want to guess why that's a problem?
16:40
Okay. as a hand up. You don't have to yell cuz there's like yes character encoding. So code pages
16:47
our files written in ASI or UTF8 the mainframe speaks EPIDC. So we have
16:53
to convert it to epsidic. So that's what we do and then we upload it and it's all good. Um for the purposes of this talk
17:00
whenever you see the blue prompt that's when we're in Linux. So we're doing something to prep. That's our
17:07
staging. If you see this prompt, that means we're on the main frame. Okay, now let's take
17:14
a look at enum. So this is that enome rex script. So what this script does is
17:20
it pulls information from memory. So it does a really good job of accessing things from memory cuz we have read
17:26
access to a lot of of memory space and it dumps information out about the operating system, about the the current
17:33
running environment. Um, and it's been built like it wasn't just me. There's other people that helped JT and other
17:38
people who have helped build this. Um, some things in memory are not documented. And so we we sort of reverse
17:45
engineer those. And what's interesting about this program is sometimes you're limited. You can't list these things,
17:52
but it exists in memory if you know where to look. So that's what this Rex script does. This Rex script pulls out all kind. I use it on every single
17:58
pentest. The next script we have, the we have is OBS enum. It is based on lin
18:03
enum. Okay. but I had to rewrite it for TCSH. And then what we did is we added a whole
18:10
bunch of mainframey type stuff to it. So you'll see us running it here in a
18:15
second. Um, and if you if you're wondering why it's going to be OMVS said here, you can come talk to me after, but
18:21
we're going to run it. It's going to we're going to tell it to send it to a report. And what's going to happen is it's going to go through and dump all
18:26
kinds of information, right? And you'll see some more mainframing stuff. So the stuff that's going to be in all caps here in a second, that's an um a list
18:34
user command from rack f, right? So it dumps all kinds of information and then we we comb through it later. Um the
18:40
other thing we always test for is egress busting. You would be surprised how often we're able to go directly from
18:47
the from the main frame behind like I have to go through like two VPNs sometimes to even touch the mainframe,
18:54
but we're able to go from the mainframe directly to AWS or some other cloud provider, right? It is it is crazy how
19:00
often that works. And so, in fact, one one of my clients, we did the test. I
19:05
wrote it up saying, "Hey, you have like thousands of ports like are are allowed to no egress filtering out to this AWS
19:11
host." And they go, "We've never we haven't used that ISP for 10 years. We
19:16
have no idea how this is routing." Right? So, anyway, it's really it's not really that it's not really that hard.
19:21
We use a Java program. The reason it's written in Java is most mainframes come with Java right by default. Um also it
19:29
allows us to control the timeout of the the packets and then we just do a port scan essentially a sin scan and then on
19:36
the Linux box we run a tool called egress tester which is a fork of egress buster and you can see all the open
19:41
ports. Okay, next picture of Chad.
19:47
He wanted me to say that I sent him this hat after I told him uh after he told me he bought a boat. That's a true story
19:52
actually. He bought a boat and I was like, you know what he needs is a dumb hat with hair cuz he does not have hair.
19:58
Okay, let's talk about some analysis. So, now that we've done the enumeration, we've gone through the enumeration. Let's look at some of the output. Um,
20:05
this is from enum.rex. Okay, and the important bits that we pull out of that
20:10
are the location of the rackf data sets and the fact that and and what hashing
20:16
algorithm they're using. Okay, Rackf uh uses either dezz for the hashing
20:22
algorithm or KDF AES there. John the ripper and hashcat both support cracking
20:29
rackf databases. And if you have read access to either of those two data sets,
20:34
it's trivial especially since we know that KDFAS encryption is not enabled. It's trivial for us to crack every
20:40
single password in that database. I think Chad was telling me a story where he downloaded the data the the database
20:47
cracked it in maybe an afternoon like two three hours had every single password for every single user. Okay. So
20:53
if you do run a mainframe please make sure you turn on KDF AES. Now when we look at the OMVS enum output
21:00
we see there's a bunch of stuff here right we can suda root without a password and
21:06
we'll talk about that in detail files that should not be world readable like someone obviously ch modded some stuff
21:12
trip 7 we can mount we have we have we can mount data sets right which you can
21:19
normally do but this one gives us more more access than we should have and this last one is we can issue the extr plusa
21:26
a command Now the other tool we ran that that gave us some interesting output was Zosshog.
21:33
Uh Zshog is based on truffle hog and it uses Reax to find secrets inside files
21:39
in Unix. And when we ran it obviously we found a password.
21:44
All right, here's the next one. God, I hate this one.
21:50
Ask Phil. Ask Phil to pronounce Java and then wiki. Java wiggy.
21:57
I don't think I say it incorrectly. All right. Next is privilege escalation. So now that we know what's wrong, right? We
22:04
know there's some vulnerabilities on the system. We definitely have to demonstrate impact especially when it
22:09
comes to mainframe hacking. You have to show impact because every not every time
22:15
I would say 99% of the time my findings are an uphill battle with the main framers. Okay? I get so much push back.
22:21
you have to show like no actually this setting is very dangerous. Look what I did. Okay, so let's talk about privilege
22:27
escalation. Obviously the first one is the super easiest one. We found storage credentials. Okay, so this could be
22:33
lateral movement. Nine times out of 10 it's not. So and I would I would love to say this is a rare thing that I've only
22:39
found once. No, I found I have found this multiple times. Okay, so do not
22:45
store password and files. Obviously, if you have to make sure the permissions are correct and make sure you test those
22:51
permissions because maybe your ESM like rackf is overriding those permissions and everyone has read access to it. Um,
22:58
so this is an example. There's an actual example from a client uh obviously not I rewrote it. It's not their work, but
23:06
it's very similar. And we found a script like this in the user's home folder and it was chodd
23:12
obviously because it wasn't working until someone did that, right? And then all of a sudden it started working. Um, it had user credentials in it. And so
23:19
super super easy hack, right guys? Mainframe hacking is not hard. It's not that hard. We just SSH in with the
23:27
username and password, right? Like this is not rocket science, right? We we type
23:32
their username, we type their password, and then we get in. And the first thing you do once you connect is you make sure
23:38
you know who you are, right? So, okay, I'm logged in as me. Um, and then we we have some fun. And then the the next
23:45
thing we do is we run the command list user. Okay, because that actually tells us what we can do. And if you'll notice,
23:51
this user has special and operation. So at this point, it's game over. We can kind of do anything we want. And the p the pentest turns from a pentest to now
23:58
an assessment because we can read everything. Uh oh, great. Uh this one's finally one not about me. He wanted me
24:05
to tell you that Mark from that like intro drove his Aston Martin into an
24:10
washed out area of a road and had to climb out the window and be rescued from the roof. I don't I asked him for like
24:17
technical quotes or like inspirational quotes and this is what he gave me. Okay, the next one we're going to talk
24:23
about is this one at the bottom cuz I know none of you know what extr
24:28
plus a does. that is a only on the mainframe command and it's it's very
24:34
important to understand. So remember we talked about APF authorized programs. So APF authorized programs are
24:41
allowed to get into supervisor state. That's what they're allowed to do, right? And that comes with a bunch of different things.
24:47
On the regular mainframe side, you have to put them in an APF authorized program library, otherwise known as a folder. On
24:55
Unix, you can actually assign programs the extra attribute A that makes it APF
25:02
authorized, right? That's all that does. Okay, so the access to control that is
25:08
BPX.file. I know it says extra, but it's file ATR.APF.
25:14
So access read access to that profile in RACKF lets you issue this command. Um,
25:20
most people should not have access to do that. Now, why is it important to get APF authorized? I'm going to walk you through what happens when you log into
25:26
the mainframe and why getting APF authorized and all this stuff is important because it's the thing I
25:31
didn't understand. So, when you log in, the first thing the operating system does after you log in is that Rackf
25:38
copies a bunch of user information about you into memory, right? And it refers to
25:45
that memory region. Think of this like your ID, like your u your ID in uh Linux, right? Right? And if you can
25:51
change your ID to something else, right? Similar concept. So it sits in memory.
25:57
Problem is that memory region is locked under key zero
26:02
and user processes only run under key8. So we cannot change this region of
26:09
memory. If we could, we could take over the main frame. Right? If there's a way
26:15
for us to change our key to key zero,
26:20
then what we do is we just replace this. It's called the ACCE. We replace our ACE with whatever user we
26:28
want that exists on the system. And now we can become someone else, preferably
26:33
an admin. But how do we change our key to key zero? Well, luckily there's an assembly
26:40
macro called mode set and we just change it to key zero
26:46
and then once we do that we to issue that macro you must be APF authorized uh
26:53
to issue that right so in Unix if we use that extr command we can give we can
27:00
make it APF authorized now what does that look like technically like what does it look like in practice so here is
27:06
what it looks like in assembly Any questions? We can move on. Great. So, really this
27:13
is the command here. Oh, that's great. The the boxes on my laptop worked. So, this is the this is their laptop
27:19
problem. So, mode set key zero. That's that's the command. If if the program
27:25
will abandon APF authorized here. So, that means crash, right? So, once it gets past that, you're golden. The next
27:31
thing we do is we issue what's called a rack route. So, this is going to build that new ACC for us. And if you'll see
27:39
there where it says uh user ID equals user len, well, that's actually down here where we have the user ID that we
27:46
want to assume the identity of. Okay. So, all we do is we write this program up. Then we we put it into uh a pro a
27:56
file in Unix. We assemble. So, if you've ever used the assembler on Linux, it's the same thing, right? the very similar
28:03
commands. Then we link it, right? Because we have to link it. And then we
28:08
make it APF authorized. Okay, so that's it. That's all the steps you have to take. And then here's a demo that we put
28:15
together. It's going to it's going to show Chad taking over my account. All
28:21
right. So, he's trying to access a file. He's unable to access that file.
28:31
He's going to run his APF authorized program. And now you can see he's become Phil, right? He's become my user ID. And
28:38
now he's able to cat that file. It's a file I wrote for him especially
28:46
cuz he is the coolest. I did not write that. This is a 100% Chad demo. All right, next picture of Chad. Uh jeez. Um
28:54
take me take Phil to a karaoke bar and get him to do regulate. You won't be disappointed. You will be disappointed.
29:01
I promise. Okay, let's look at the next one. Sudar root. I know it says pseudo root.
29:06
There's not really a concept of root users on the main frame. Okay, so on the
29:12
main frame we actually call it super super user or UID0. Okay, the problem is
29:19
you know on Linux if you get you know root like UID0 it's game over for that
29:26
that box, right? You can do anything you want. You can change anything you want. The world's your oyster. That's not
29:32
really true on the mainframe. Yes, you have UID0 in Unix, but that doesn't
29:37
convey anything outside of Unix. Like when you log in that address space that we talked about earlier in key zero,
29:43
even though you you sue up to root, it doesn't change your actual user and
29:48
address space in the rest of the main frame. So here's an example. So here I am.
29:56
My user ID is Phil. I type the sue command. Notice I don't have to provide a password. So I type the sue command.
30:03
Now I'm a different user theoretically, right? But when I do the rackf command lu, I'm
30:11
still me. But that's fine. There's a billion ways around this. This is just one dumb
30:17
example. I'm sure if you're creative enough, you can find a thousand different ways to do this. Um, but the easiest thing for us is just to just to
30:23
add an SSH key for an admin. So, and that's really easy. So, we pick Mark, of
30:28
course, and we make the SSH folder for him. We then make the authorized key
30:33
file for him. Make sure the permissions are good on that file. And then we put our public key in there, right? And
30:40
that's what it looks like. Everything's fine. Everything's good. And then we just SSH in as them, right? With our
30:48
private key that we generated ourselves. And then we're logged in as Mark. And if you look at Mark, Mark is special
30:55
operations. So it's game over again. So I don't know if you're noticing a trend, but we have like our two goals is either
31:00
to get special operations or APF authorized. Those are the two things. All right, next one.
31:08
The lucky among you might get to play crafts with Phil later. Damn, I'm sad I'm missing that. Oh, thanks, Chad.
31:14
Okay, next. This mount one. Okay. When you look at the the oper when you look
31:20
at the mount points, if have you if you've ever mounted an ISO in in Linux,
31:26
it's very similar, right? Think of it or almost like volumes in a container,
31:31
right? So, you take every the whole file system is based on data sets, right? And you mount those data sets into uh a
31:40
location on the file system. That's all it is. Now if we have update access to
31:46
either of these two profiles right super user.files do usermount or super user.files.mmount
31:53
what that means is we can mount a data set and preserve the APF bit and the set
32:02
UID bits. If we have read access to either of those profiles then those bits are ignored. But so so and as you saw in
32:10
our output, we did definitely did have access to super userfiles user mount. So what we do is we create a payload on a
32:20
mainframe we own, right? I have a main frame at work. Chad has his own mainframe at his work. So we create a
32:26
data set that we we that's going to be malicious. Then we create our programs, the ones
32:32
you just saw. We can make them APF authorized in our own file in our own system, right? we can craft this
32:37
payload. We unmount it. We package it up with some JCL. We transfer it to the
32:43
target mainframe and then we receive it and do all the things and then we run our tools. So this is the JCL to mount
32:50
that data set. Might look very it's very familiar to like the mount command, right? So we have, you know, we to mount
32:56
the hack the planet and then we have a mount point that goes to slashtemp/hack the planet. And then when we look at the
33:03
output, you can see here this one maintain the set UID bit. So now we can
33:09
pseudo routt get UID0 byp without having to do any of that fancy stuff having
33:15
access to uh bpx.s super user. And you notice these there's programs here that are APF authorized. Even though we don't
33:22
have the ability to do that on the target mainframe because we could mount a file system, we could do that. Now
33:28
from here the demos are exactly the same as the other two demos, right? We can either modify people's home folders or
33:34
because of RPF authorized become any user we want to become. Uh great. Uh he's wanted to tell you
33:43
that he grew up on a farm and the tractors all ran on cobalt. I highly doubt that. But all right, let's talk
33:50
about buffer overflows on the mainframe. Uh you know that slide earlier with
33:56
Ralph and it says you can't do buffer overflows on the main frame. That's a myth that has been debunked multiple
34:03
times and I gave a talk last year at share shares being the main mainframe industry conference where someone in the
34:10
audience was like telling me you can't you can't do what you're telling us you can do and I'm like guy the whole talk
34:16
is about mainframe buffer overflows and I'm teaching you how to do it and he still wouldn't believe right so there's
34:21
still this myth that you can't overflow buffers on the mainframe it is so false anyways lots of programs in Unix are
34:29
written written in C. C is not a memory safe programming language. Okay. And so
34:34
if you have a C program and there's a buffer overflowable variable and it's
34:41
APF authorized now we can execute APF authorized code
34:47
because of this program. Right? How do we find APF authorized programs? Um oh
34:52
boy, this red box is way off. Um so how do we how do we author authorize find them? We use the - exta. This is a find
35:00
command and you use find and then d- exta. That's extra attribute a that will show us all the APF authorized programs
35:07
that exist on that LPAR. This is just one screenshot. It kept going forever.
35:13
Am I saying that all these are vulnerable? Probably not. Probably a whole bunch of them are probably not vulnerable at all. But I know
35:19
researchers who have found vulnerable programs that were APF authorized. Okay. Unfortunately, we have like 10 minutes
35:26
left. Getting into the complexities of writing a ZOS buffer overflow would take
35:32
hours of content to get you to understand it. Fortunately for everyone here, there is hours of content
35:40
available to you to learn this on your own. Jake Leel gave a great talk at
35:45
Defcon 30 on how to find and exploit ZOS buffer overflows and explain the memory
35:53
layout and all that stuff. Don't take a picture yet. There's like two more things to go through.
35:58
Uh Chad gave a talk. In fact, this is this if he was here on stage, this would have been our 10 year anniversary giving
36:03
co talks. Uh we gave a talk 10 years ago and part of that talk he explained how
36:10
he could do buffer overflows in ZOS Unix and Jake and I defcon 30 we taught a
36:17
class on mainframe buffer overflows and that class is freely available. You go
36:23
if there's a Docker container, you run it and it walks you through step by step
36:29
how to do a mainframe buffer overflow so that you can generate something that looks like this. Okay. Did anyone get
36:36
their picture? I saw some people trying to take pictures. You want me to go back? Everyone's good. All right. So, so
36:41
you this this is doing like the stuff we were talking about earlier, right? The
36:47
rack routes and all that. So, this is machine code that we're going to use to overflow the buffer. So, that's shell
36:53
code. We don't call it shell code, but it's shell code. Uh, all right. Here we go. Here's the
36:59
next one. Um, he wanted me to say that Phil and I had a tradition of going to piano bar after
37:04
every evil mainframe training. Ask him about the fishbowls. Uh, be my guest.
37:10
It's fine. Okay. Let's talk about some honorable mentions that I see on pentest. So remember how we mentioned
37:16
that you can enhance your security by letting the ESM
37:22
have like more security on top of the file system, right? I have been on
37:27
systems where that was done improperly. And while it looked like I didn't have read access to some folders or files, I
37:35
could read every single file on the entire in the entire ZOS Unix because it
37:42
was not done. it was not uh secured properly. Uh world this one's fun. There was a
37:48
there was a shell script in bin that was worldw writable that was chod 7. So I
37:54
and it was it was in / etc/profile. So every time someone logged in it ran so I
37:59
just modified it a little bit and then when a user that was special logged in
38:04
it then made my account special. Uh this one is not really an exploit or anything like that but this happened too
38:10
many times. I want to let you know about it. Please don't make your logs that go to the sim world readable or writable
38:17
because I've been on like two or three mainframes now where the staging folder in Unix and the files in that folder are
38:24
worldw writable. Okay, so please don't do that. Uh last one is uh I was I was
38:29
pentesting mainframe. I couldn't access much in zos Unix but they had a web app that had an LFI vulnerability a local
38:35
file included and then I could read a whole bunch of files. So, I was like, I could see where they were, but I couldn't read them. But the web app
38:40
could. Now, I would be remiss if I didn't tell you how to prevent and detect these,
38:47
right? I hate I hate watching talks at Defcon. It's like, oh my god, that's terrible. What do we do about it? Too
38:52
bad. That's not what I'm here for. That is what I'm here for. I'm going to tell you how you prevent it and how you
38:57
detect it. So, first prevention, right? Review your file permissions. It is you
39:04
can just run a find command to find everything that's been chod 7. Okay, please check your like every single
39:09
pentest I do, I have file permission findings. Please check your file permissions.
39:15
Review and control access to these profiles in your ESM. They are the same profiles. Doesn't matter if you're on uh
39:22
ACF2, top secret, RCF. Make sure access to these profiles is limited. In fact, I
39:28
would argue no one needs to have these this access unless it's a break glass account,
39:34
right? Test your file permissions. Even though the file permissions look correct, there
39:42
might be something in your ESM that's overriding those permissions.
39:47
Okay, now let's talk about detection. Monitor, we put we say log, monitor your
39:53
SMF messages. SMF is the logging facility for ZOS.
40:00
Someone who's using BPX.s super user. So every time you type sue, the operating system goes and says, "Hey, does this
40:05
user have BPX.s supersup user and then it says yes, right? Or it says no, right? If it says yes, you should
40:11
probably be monitoring for that. Who's using it? Why are they using it?" Same with the BPX. ATR.APF.
40:18
No one should really have that. That should be something that you you're installing updates or patches, but no
40:23
one should just have that as a blanket access, right? If someone is using it, it should be traceable back to a request
40:29
or a ticket of some sort. And then obviously the mount commands again users
40:35
shouldn't be mounting things as a super user. That should be all done by the operating system during startup right
40:40
like no one should really have that access unless it's like a break glass situation.
40:46
Detect large number of unauthorized attempts access files. You'll understand how like it will log every failure when
40:55
I when I run my own VSS enum script. It's looking for files and it'll tell you like access access denied. Those all
41:01
get logged somewhere, right? No one has ever come to me after a pentest and be like, "Hey, did you try to access like 30,000 files?" Never. Cuz no one's
41:08
monitoring it. Uh detect multiple obviously look if if you're trying to see someone do connections out to AWS
41:16
on your like firewalls and whatnot from the mainframe, that's probably a good indicator of compromise, right?
41:21
Something to check for because the main frame should have very well understood and well-known patterns of connectivity.
41:27
There should be nothing exciting happening there. And then we're going to talk about the Unix file system auditing. This is like
41:34
very unique to to Zos Unix. So when we run Zos Unix and when we're in Zo and we
41:41
issue ls with a capital W, we we get these new this new column here, right?
41:49
And this column is the audit column, right? That's what's happening here. So
41:54
let's take a a closer look. It's it's split up into two parts. The
41:59
first part is user controlled. So if you have read, write, execute access to that
42:06
file, you can modify those settings. The other three are admin controlled. So if
42:15
so, if an admin wants to set so you could set it as like, hey, I don't want any audit records for this file. But
42:20
your admin could set something that says, "Hey, I want to know anytime someone changes that file, right?" And
42:26
you as the user have you cannot change it back. This is the default. So f FFF
42:32
for fail and then no admin control. This is the default for every file created in
42:37
Zos Unix. If you list any file, that's the default. And the way it's broken down is very
42:44
Unixy read, write, execute. So if I try to read the file and it fails, it's
42:50
going to write an SMF record. If I try to write the file and it fails, it's going to write. And if I try to execute,
42:55
it's going to do that. Now, much like CH, you can chify, you can ch audit a
43:01
file. And so use the ch audit command. And what we're going to do is we're going to say I want success and
43:07
failures. And now when we run that same command, you can see now they say all.
43:14
So now I have all anytime someone accesses that file, anytime someone
43:19
writes that file. Now this is a little extreme. Don't do this for every file, but you you should know what files are
43:26
critical to your mainframe. And you should know, hey, if someone makes a change to this file, we want to know
43:32
about it, right? Things in slash, etc. Probably a good idea to know who's mucking around in slash, etc., right?
43:38
Okay. So with that, this is this we're we're nearing the end of the presentation. Uh I have to do some shout
43:45
outs to you know because I'm up here because of the efforts of a lot of other people. So first I want to say thank you
43:51
to Defcon for having me come here. I really appreciate you all. Um the mainframe hacker community when Chad and
43:58
I started doing this the mainframe hacker community was two people Chad and I. Okay. Over time that has grown. The
44:07
second the third member was Henry Wizard of Zas. And over time that has grown. So now there's like a good two dozen of us
44:15
and we chat and we all know each other and we share ideas and whatnot. So I have to huge thanks for them. Um the
44:21
Moshix Discord. So if you're look if you're not a mainframe person and you're like oh man this is interesting. Go
44:27
watch Moshix's videos. Go to the discord. It's super welcoming. It's not
44:32
very Do not go to mainframe forums. It is the most adversarial place on earth.
44:37
Go to the MotionX Discord. It's super chill. Everyone's there to help. uh the mainframe cyber security community. I
44:43
went to share share being made the mainframe industry conference and I was so nervous the first time because I
44:49
thought they hated me and all these things. Uh in fact a major vendor threatened to pull out if I spoke at
44:54
that conference kind of thing. But the mainframe cyber security community at that conference is the most welcoming and amazing community there. So huge
45:01
shout out to them. Um and I do want to thank my co-speaker Chad for like you
45:06
know helping me out with this talk and I really I do really wish he was here. If you want to contact, if you want to
45:12
reach out to me um in any capacity, if you have questions, I'm always I'm always interested if people have ideas
45:18
or questions. I will take any pull request within reason. So if you want to look at my code, it's not good, but it
45:24
works right. So if you want to tick sometimes, so if you want to take a look um and reach out to me, that's totally
45:29
fine. And I'm going to leave the talk with the last quote from Chad. So,
45:35
remember when I said there were two members to the hack made from hacker society and then Wizard of Zas joined us. That's Wizard of Zas in the middle
45:41
there. So, so that's, you know, it's it's a tight-knit group of people. So, this is what he wrote for me. I'm going
45:46
to try to get through it, uh, cuz it's a little long and I love it. U, so, dear Phil, in all seriousness, I am really
45:53
sad I couldn't be here even though I know that you absolutely kicked ass and I do not you do not need me here to do
45:59
so. Uh, you've been one of my best friends and partners in crime for a decade. I would not be here where I am
46:05
without your friendship and knowledge and willingness to put up with my [ __ ] I cannot wait to see what the next decade of hacking the Gibson with you
46:12
brings. Uh, and with that, I want to thank everyone for being here. And that's the end of my talk.
46:19
Yeah, I heard that.