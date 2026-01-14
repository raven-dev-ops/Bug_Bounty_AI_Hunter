0:00
All right. Uhoh and welcome to my talk on mastering Apple's endpoint security.
0:06
So today we're going to talk about all things related to Apple's endpoint security. We are going to start with
0:11
some basics but very quickly we will then move into some more advanced topics
0:16
as well as cover some nuances and pitfalls really shed some light into
0:22
what I think are the darker corners of endpoint security.
0:27
Super stoked you're all here. Uh I imagine those of you who are defenders,
0:32
malware analysts, perhaps those writing security software, the content of this talk, its relevance should be readily
0:40
apparent. Uh but if you are a attacker, a hacker, a malware author and are
0:46
targeting Mac OS, cool. You know, it's Defcon. All are welcome. Uh I think this talk will be very relevant to you as
0:53
well because as we'll see endpoint security really provides defenders the tools to detect even the most advanced
1:00
malware. So again if you're a hacker this might cause you some consternation. So having a in-depth understanding of
1:06
what the defenders have in their arsenal I think is re very relevant.
1:12
My name is Patrick Wardle. I am the founder of the Objective C Foundation.
1:17
More recently in parallel, I am also the co-founder of W, where we are building
1:23
core Mac OS detection components to integrate into larger enterprise security products.
1:30
I'm also the author of the art of Mac malware book series. I mention this here
1:35
because in volume two there are two full chapters dedicated solely to endpoint
1:41
security. So, if you find this talk interesting and you want to dig more into the content of what we're covering
1:47
today, I recommend reading that. And this is not a sales pitch because good news is this book is 100% free online.
1:57
So, let's start with some basics. Those of you who perhaps have dabbled in endpoint security, this might be a
2:02
little bit of review, but it's important for us to all be on the same page before we delve into more advanced topics. So,
2:10
what is endpoint security? Apple has a fairly succinct definition. They say it's a C API for monitoring system
2:18
events for potentially malicious activity. For me, what I love about
2:23
endpoint security is really for the first time, it's a framework that Apple has released specifically for third
2:30
party security tools. And I cannot stress the importance of this enough. Some of you I look around you look to be
2:38
perhaps my age or a little bit older. So some of you might have been writing Mac security tools before endpoint security
2:44
was released and you know that sucked because there were no APIs dedicated to security tools. Something like creating
2:51
a simple process monitor was very very difficult. Now though with endpoint security it is a breeze. So thank you to
2:57
Apple for releasing this. Myself and other tool developers we are forever indebted to you. While I am heaping some
3:04
praise on Apple, which is maybe a little bit rare for me, I also want to give a shout out to them for their
3:09
documentation. Unlike some of their other frameworks, Endpoint Security is actually fairly well documented. If you
3:15
go to their developer site, there's a whole section on that, even sample code. They also ship a neat utility ES logger
3:22
that's built into Mac OS that allows you to explore endpoint security directly
3:28
from the terminal. Now though, if you talk to anyone that really does any in-depth tool
3:35
development using endpoint security, they will say, "Okay, ignore all the online documentation, go to the header
3:42
files." And so I want to instill that wisdom upon you as well. So there's three main header files. These will be
3:49
found in the SDK directory under endpoint security. You have ESclient, ES message, and ES types.
3:56
As we can see on the slide, these are not normal header files. They can they include for example asy flowcharts
4:03
describing very complicated parts of endpoint security. So again, thank you to whoever the Apple developers who
4:09
poured their heart and soul into these header files. Super indebted to them as well.
4:15
Another takeaway or point I want to make early on is if you are developing security tools for Mac OS, you should be
4:21
using endpoint security. Not only is it recommended and supported by Apple and anytime Apple recommends and supports
4:27
something, use it. I've been on the other end of that trying to do something a little different, especially before
4:33
endpoint security, that always figuratively bit me in the butt when Apple would change something. For
4:38
example, when a new version of Mac OS came out. Also, Apple continues to invest and improve endpoint security.
4:45
So, it just gets better and better. And then finally, as we will see, endpoint security is insanely powerful, giving us
4:52
unparalleled insight into activity on the operating system, which means even the most sophisticated malware will be
4:59
observable. So again, if we use endpoint security, it really as defenders gives us a great leg up.
5:07
Let's now talk about writing an endpoint security tool. Conceptually, it's actually pretty straightforward into
5:13
basic steps. In subsequent slides, we'll show code how to do this, but for now, let's talk about how to do it
5:19
conceptually. So, the first thing you're going to do is going to be to create a endpoint security client. This is
5:25
important because all subsequent endpoint security API calls need this
5:30
client. You basically pass it around. So, step one is to create this client. We'll see that you create this client
5:36
with a handler block. And I will repeat this several times that this handler block receives the events of interest
5:43
that you subscribe for. We'll get into that a little bit more. Once you have initialized created a endpoint security
5:50
client, you specify and subscribe to events of interest. So imagine we've uh
5:56
we're interested in tracking uh process spawns. We want to get notified anytime a process spawns anywhere on the system.
6:03
For example, to check if it's malware, something it's trusted. We can do that with the notify exec event and we'll
6:09
talk more about events very shortly. But the idea is once we've created a client
6:15
and subscribed to this event, anytime a new process is started either by the system, by the user, by malware, by an
6:21
exploit, doesn't matter. New process, it means we, our endpoint security client, will get a notification and an endpoint
6:28
security message telling us that just happened. Super powerful stuff.
6:36
Let's now talk about these endpoint security events. These are the ones that you can subscribe to. So these are
6:44
declared in one of the header files, specifically es types.h. There's a large
6:49
structure that currently holds over 150 events that you can tell endpoint security you are interested in
6:55
subscribing to. These range from process events that we just mentioned to file events, USB activity, all sorts of
7:03
really interesting events. And Apple continues to add more. Generally, these events fall into two categories. There
7:10
are notification events. These are events that are delivered to you after
7:15
the fact that something has occurred. So, for example, on a previous slide, we saw the notify exec event. This will be
7:23
delivered to you anytime a new process has started. But it's important to understand that it is reactive. It's
7:29
after the fact and you can't really do anything about it. It's just a notification. Still, this is very
7:36
powerful. If you want to, for example, build a passive process monitor or file monitor. Notification events are your
7:43
friend. The other category are the more powerful authorization events. These
7:49
actually are delivered to you before the event occurs and the operating system actually pauses or holds the event until
7:56
you explicitly approve or deny it. So we'll see for example there's another process event off exec that you can
8:04
register for and if you register and subscribe to that whenever a new process is about to be started the operating
8:10
system endpoint security will pause that ask you if you want to allow or deny the process and if you allow it it will
8:17
allow the process to continue but if you say no it will actually prevent the process from starting in the first
8:23
place. All right, so let's talk about actually
8:28
creating an endpoint security client. Don't want to go through all the code, but you can see it's 15 lines, nothing
8:34
too in-depth. Basically, first we import the endpoint security framework. We
8:40
declare an endpoint security client. We define a handler block, which we'll talk
8:45
about more in a subsequent slide. Most important though, at the bottom line 15, we see we invoke the ES new client API.
8:54
This takes a pointer to the endpoint security client that will be initialized and then the handler block that will be
9:01
invoked automatically by endpoint security anytime matching events occur anywhere on the system. Now this is the
9:08
first endpoint security API you're going to call. So it's very important to check the return result from this because
9:14
we'll talk briefly shortly about some of the prerequisites that Apple leverages on us if we want to use endpoint
9:20
security. But for example, this API can fail if we don't have the right entitlements, privileges or permissions.
9:30
Once we have created a endpoint security client, next we need to tell endpoint
9:36
security what of those 150 or so events we are actually interested in and then
9:42
subscribe to them. So this is done via the ES subscribe API call. You can see
9:47
it takes three arguments. The first is that initialized endpoint security client. Then an array of events. Here
9:55
we're only asking to subscribe to one, the notify exec event. And then we have to pass the number of events in this
10:02
array. Recall that endpoint security is a C API. It's very low level. So a lot
10:07
of times you're going to see APIs that take an array, an account, a string, and a length, etc., etc. These are very
10:13
low-level CS isms. Now once we've subscribed to this event as I mentioned anytime the matching
10:19
events occur we will get notified about them.
10:26
So when an event occurs that matches one of the ones we've subscribed to endpoint security will deliver us a lovely
10:32
message indicating that a matching event has just occurred. Here is the message that is delivered.
10:39
It's rather a large structure with a lot of members. We're not going to go into all of them, but I do want to mention
10:45
two or three important ones here. So, first we have what I like to call the responsible process. And this is the
10:52
process that is responsible for triggering the event. So, imagine we've registered for file IO endpoint security
10:59
events. And imagine we are now monitoring the file system to detect anomalous or unusual events. Say
11:07
something accesses the keychain database. The question is, is that the user? Is that the trusted keychain app
11:14
or is that a stealer that's trying to grab your passwords and certificates? Well, the good thing is when we get the
11:20
file IO event that endpoint security delivers to us, if we examine the responsible process, it will tell us who
11:27
done it and we can see if it's the user, something trusted or something malicious like a stealer. We also get an event
11:34
type. You can subscribe to multiple events in the same endpoint security client. So this one will tell you what
11:41
event this message belongs to, what type. And this is important because the event data is event type specific. If
11:48
we've registered for say process and file events and this is a process event,
11:54
the event structure will be related to the process. For example, a PID and a path. If it's related to a file event,
12:00
it won't have a PID, but it will have things like the file source and destination path.
12:07
Now we talk about the all-important endpoint security handler block. As I mentioned, this is invoked automatically
12:13
by endpoint security anytime a matching event occurs anywhere on the system. This is where you put all your logic to
12:20
do whatever you want to do to process that event. If you're writing a simple process monitor or file monitor, in this
12:27
case we just print out some of the information, the responsible process, etc., etc. If you're trying to detect
12:33
malware, this is where you would have some huristics, for example, to examine what the event is, who did it, and if
12:40
it's malware or not. Now, the last thing we need to talk
12:45
about are those pesky prerequisites. So, endpoint security is an insanely powerful framework that gives you
12:52
essentially full access, full observability of everything that's happening on the operating system. Apple
12:59
understandably says, "Hey, this is super powerful." And so from a privacy point of view, we just don't want any process
13:05
using endpoint security. So they protect it with an entitlement that you have to ask or rather beg Apple give you. And
13:13
without this entitlement, you can't write endpoint security tools or at least you can't deploy endpoint security tools. So once you beg for this
13:20
entitlement and make a sacrifice the Certino if they grant it to you, you were super stoked. You can then create a
13:28
program that uses endpoint security. notoriize it, entitle it, and then deploy it to your users. Your your users
13:34
though are going to have to run it with root privileges and either grant the utility or the terminal full disk
13:40
access. Again, this is just to essentially protect users from inadvertently uh or something malicious
13:47
using endpoint security. Okay, so that is a wrap of an introduction to endpoint
13:53
security. Hopefully, if you'd even never heard about endpoint security before, you understand at least conceptually how
13:59
to create an endpoint security tool. So, now I want to talk about some of the more advanced topics and also some of
14:06
the nuances and pitfalls. Many of these have bit me figuratively speaking in the
14:11
bot and so I want to share you share them with you so you can avoid my blood,
14:16
sweat, and tears. So, let's start with caching which is a nuance but very
14:21
important optimization. So caching is related to authorization
14:28
events. So remember we had the authorization events which are events that the operating system will
14:34
essentially disallow them until your endpoint security client tells tells the
14:40
operating system to either allow or deny it. So for example, we have an off exec
14:46
event to authorize new processes or deny ones we don't want. So the way you
14:52
respond back to the operating system is by invoking the ES respond o result API.
14:58
This takes your decision a yes or no and then a very important flag which tells
15:04
endpoint security whether to cache the response or not. If you tell endpoint security to cache the response,
15:10
subsequent process executions of that same process will not result in endpoint
15:16
security sending you another message. It basically says, "Yo, I got it. I'm gonna cache this. I'm not going to ask you
15:22
again. So, let's show a specific example of a
15:27
tool that should have used caching but didn't. And I'm going to pick on this tool because I wrote it. So, one of the
15:33
tools I've written is called block block. It monitors for persistent malware, but it also has a neat feature
15:40
that if you turn on notoriization mode will block any process that is not
15:45
notorized. What is notoriization? It's essentially a Apple security mechanism
15:51
that requires developers to submit their compiled binaries to Apple. Apple then
15:56
scans them for no malware. If none is found, Apple notorizes it, essentially giving it a stamp of approval. Then at
16:03
runtime, Mac OS will check to see if a process or program is notorized or not.
16:09
Now, obviously, the vast vast vast majority of legitimate software is going to be notorized, whereas malware often
16:15
isn't. Malware authors are not keen on giving their binaries to Apple before they deploy them. So this is a very
16:22
powerful heruristic that can block most malware very simply and very generically. And yes, Mac OS does try to
16:29
also prevent non- notorized code from running, but there's a lot of loopholes. Mac OS is actually very lenient, which
16:35
is why block takes a more draconian step. So in terms of implementation,
16:40
block uses endpoint security. Specifically, it registers or subscribes
16:46
to the off exec event. Then whenever a program is launched by the user, by the system, by whatever
16:52
endpoint security pauses that, asks block. Block block checks if it's notorized or not. And if it is, it says
16:59
cool, you can run. If it's blocked, it says no and tells the user about this fact.
17:04
Here's some of the code from block. Don't worry about reading it all. It's more for a reference if you're interested. Basically, block uses
17:11
Apple's code signing APIs to check if something is notorized. And then at the bottom, you can see it invokes that ES
17:17
respond off result telling endpoint security to allow or deny. I took out the allow code. It's essentially the
17:24
same as the deny code. But the key is that block did not cache the result. Why
17:29
not? Patrick didn't read the header files. Also, process launches are not that common. Notoriization checks are
17:36
not that CPU inensive. So in my testing I didn't see a problem. Well of course I
17:42
deployed block and shortly thereafter I started getting some bug reports especially from people who were
17:47
compiling large programs large software projects. They said hey Patrick block is
17:54
causing the CPU to spike. Very quickly I realized what the problem was. When you compile a large software project, uh
18:01
especially if it's like Objective C or Swift code, the compiler is invoked again and again and again and again to
18:06
compile each file. Since block wasn't caching the result, this means endpoint security would ask block again and again
18:13
and again if it wanted to allow the compiler. Obviously, block should have
18:19
checked the compiler once, said, "Yeah, this is a signed notorized trusted Apple process, cached that response, and then
18:25
endpoint security would have never asked block again. but it didn't. Turns out there's some
18:32
more nuance problems with caching. And so block not caching revealed a more
18:38
subtle problem. So I got another bug report saying, "Hey Patrick, I have block and jtrotect installed on my my
18:46
computer and I noticed that when block is running, J protect CPU utilization goes through the roof." I was like,
18:52
that's super weird. Like why is blockb block impacting J Protect? So turns out that block and jav protect both use
19:00
endpoint security which is fine. What JF does is also subscribe to the O exec
19:06
event also no problems there. What JF did though it was for every new process launch they would perform some very CPU
19:13
inensive actions hashing the file running a full Yarao scan all sorts of things but then J cached that. They
19:19
basically said, "Okay, we're okay doing a one-time very CPU inensive thing, but
19:25
since we cache it, we will only do it once." Well, unfortunately, the endpoint security cache is global. And there is a
19:32
nuance that if there is another endpoint security client on the same system that is not caching the results, this
19:38
actually undoes the caching even for the other client. which meant that because block was not caching, this meant that
19:45
JF was receiving all the same endpoint security messages again and again and therefore were performing the same CPU
19:53
inensive actions over and over. Who's at fault here? Kind of everybody. I will
19:59
take full responsibility. Block should have been doing caching. I would argue the fact that the endpoint security
20:04
cache is global. I understand why Apple did it. It's kind of a very simple way
20:09
uh but does have some problems. And then I think J should have taken the step of implementing an internal cache because
20:16
if some other client doesn't implement caching ultimately it would impact them. And even if a new client comes along,
20:23
Apple says that the cache would be invalidated. So if you're writing your own security tool, make sure you implement your own cache as well. All
20:30
right. So you're like, Patrick, I get it. I should use cache. Not so fast. Nuances, nuances, nuances. That's really
20:36
the theme of this talk and Apple's endpoint security. This is because caching may be broader than you think.
20:43
So let's look at what it means for off exec events. Turns out caching is based
20:48
on the binary itself, the file IODE. So let's look at the slide. Imagine a
20:53
developer is installing homebrew and he does that via bash and curl the
20:59
recommended way. If there's an endpoint security client that is examining new processes, it will see bash and curl
21:04
being executed. it will approve these because they're trusted notorized processes. And if it was a person who
21:10
came to Patrick's talk, it was like, okay, I'm going to cach these because caching is very important. Well, the
21:15
problem is if later malware uses bash or curl, endpoint security will not deliver
21:20
a new event because bash and curl have not changed. That is to say, caching does not take into account the
21:26
arguments. So, what you really should do is avoid caching binaries where command
21:32
line arguments control the behavior. for example, curl, python or script interpreters. So again, always some
21:39
nuances. So that's caching. And now let's transition to talking about scripts and
21:45
their interpreters. This is important because a lot of Mac malware even today is distributed to end
21:51
users as standal standalone scripts. For example, we have Joker Spy, a malicious Python script. Sigin, which was a
21:59
malicious bash script. There's many of these. Now, if you've been following along so
22:05
far, you've heard me talk a lot about the responsible process. And this is because endpoint security events are
22:10
tied to the process that essentially triggered them or created them. And this
22:16
is usually all well and good, but not in the context of script interpreters. So,
22:22
imagine the user inadvertently executes Joker spy. Well, endpoint security will
22:27
deliver a process event if someone has subscribed to it, but it won't be for the actual script. It will be for the
22:34
script interpreter. And if you think about it, we actually don't care about the script interpreter at all. We don't care about Python per se. What we really
22:41
care about is the script. We want to perhaps scan that to see if it's malware. Run some huristics against it
22:48
to see if it's something malicious and if so block yes Python but because of the script.
22:56
So Apple realized this after endpoint security was released and in version 2.0
23:02
of endpoint security they added a script member to the exec structures. These are
23:08
the structures that describe processes and this is awesome. So now as we can see on the slide, we can write code that
23:16
can extract the script from a script interpreter. Note two things though.
23:21
First, we check the version to make sure we are executing on a compatible version of endpoint security. This is very
23:26
important to do anytime you use these newer methods because you don't want to crash if the user runs your program on
23:31
an older version of Mac OS. Also, then we check to make sure it's null because for most processes that don't have
23:37
scripts, it's going to be blank. But for script interpreters, it should be set, meaning we get the script, which then we
23:43
can scan to make sure it's not malware. And this appears to be all well and
23:49
good, right? Now, spoiler, more nuances. So, if we execute Joker Spy, it's a
23:55
malicious Python script named sh.py. We can see the first invocation where we
24:00
execute it directly. This generates an endpoint security event. We look at the script member that Apple now sets and
24:07
indeed it is the path to the malicious script which we can now detect as malware and block it terminating the
24:14
Python process protecting the user from infection. Well, if we execute it again, this time
24:20
via the script interpreter. So, Python and then script.py,
24:25
we can see that as expected because we're not caching script interpreters, we get another process event. However,
24:32
in this case, the script member is is null. It's blank. And so, we can't detect that. And the malware is free to
24:38
run. So, what's going on? Well, if we go back to the header files,
24:44
which recall are the source of all answers to everything related to endpoint security, we see a very short
24:50
comment that says this field is only valid if a script was executed directly and not as an argument. Which means as
24:56
we saw in the previous slide, if the script is executed directly, the script member will be set. But if it's executed
25:03
via a script interpreter, it will remain blank. This is kind of a huge shortcoming and something that we really
25:10
all need to be aware of. Now, if we are aware of this, we can solve this in
25:15
various ways. For example, if we see a script interpreter, we can ourselves
25:20
manually enumerate all the arguments. And for those that are file paths, we
25:25
can treat those as scripts. So that's scripts and more nuances.
25:32
The next topic I want to talk about deals with authorization deadlines. And this is arguably the most important
25:39
topic because if we don't get that right, we're going to get killed like for real.
25:46
So let's briefly go back and touch on off events. So we talked about this a
25:52
few times but let's focus on the offexec event. Recall that if we subscribe to
25:57
this event anytime a new process is about to be spawned endpoint security will first come to us and ask us if we
26:06
should or we want to allow or deny the process while we are making a decision. That
26:12
process is going to be essentially suspended or not run. And so Apple says,
26:18
"Okay, third party developers, we're going to give you a little bit of time to make your decision, but if you take
26:23
all day, like this is going to impact the user experience." And you know, Apple is not stoked about the user
26:28
experience being impacted. And so what Mac OS does is eventually if you don't respond quick enough, it will it'll nuke
26:35
you. It'll terminate you. Not like yuyu, but your client, right? And it will generate a crash report and at least
26:41
it'll explain exactly why. So, you might be thinking, "Okay, Patrick, yeah, yeah, I get it. I'm going
26:47
to make sure I respond fast enough uh so Apple doesn't kill me." But what if you're waiting on a user? So, back to
26:54
block. When it detects a non- notorized process, it actually asks the user, "Yo,
27:01
what do you want to do? What if the user is out to lunch? What if the user is not paying attention?" Ah, they don't
27:06
respond. Well, is Apple going to kill us? Yeah. So, what is block supposed to
27:12
do? This is where endpoint security
27:18
deadlines come into play. So recall that for every endpoint security event, we
27:23
get this big endpoint security message that has a lot of metadata. But one of the things it has for these off events
27:29
is a deadline. If we go to the header file, we can extract some important information about what these deadlines
27:35
are. First, it's a mock absolute absolute time. Next slide, we'll talk about what that is. It also says failure
27:42
to respond, you will get nuked. Okay, Apple, we get it. And then thirdly, it says the deadline can and does vary
27:49
between messages. And we can confirm this if we create a simple program that just spits out the off deadlines. We can
27:56
see that for system processes, it's 3 or 4 seconds. For application, it's about
28:01
15. So that's a decent amount of time. Favor, don't ask Apple to increase this.
28:07
There's a funny quot uh post where someone does and um Quinn the Eskimo who is my favorite Apple employee. He is an
28:14
OG that responds to everyone's technical questions um on Apple forums and he I
28:19
don't know if he was joking or not but he's like every time someone asks to make the ES off deadline longer, Apple shortens it. So don't ask Apple because
28:26
we like that it's not super short so far. So let's talk a little bit more about
28:32
this for two reasons. First, it is a mock absolute time. I have no idea what
28:38
that was. I read Apple's documentations. It says a value of a clock that increments. Like, okay, that doesn't
28:44
tell me too much. More importantly though, most of the APIs we want to use to actually take into account the
28:49
deadline nancond. So, we need to convert this from a mock time clock increment
28:56
value to something that we actually understand that the APIs want, which are nanconds. So, what did Patrick do? Patrick said,
29:02
"Okay, cool. like I will convert mock time to nanconds and that was all well and good until Apple silicon came along.
29:09
With the release of Apple silicon, Apple published a document say called addressing architectural differences.
29:16
It's just gripping content. Of course, Patrick didn't read this, but this was problematic because one of the few
29:21
things Apple says you must do very carefully on ARM systems is convert mock
29:26
times to nanconds. You cannot do that directly. You're supposed to use a timebased information. Uh, I don't know
29:32
exactly what that means, but Apple does provide a nice helper function that we can invoke to convert mock times to
29:40
nanoseconds. So once we have that, here's some code to ensure that we respond to the
29:47
deadline. Again, this is more for research uh resources. I don't want to stand up here explaining code all day.
29:52
That's not that exciting. But what we can see is we essentially compute the delta. That is how much more time we
29:59
have in the deadline. Is it 3.5 seconds? Is it 15 seconds? We then subtract a little bit of time from this because we
30:05
want to make sure that we're responding before the deadline. And then at the bottom of the slide, we create a
30:11
dispatch semaphore that will time out right before the deadline to make sure if the user, for example, hasn't
30:17
responded, at least we programmatically respond so that Mac OS does not kill us. Now, there's probably other ways to do
30:23
it. This is just the approach that block takes. So again, that's off deadlines.
30:28
Make sure you respond to them quickly enough or Apple will nuke your client and not restart it. Meaning the system
30:34
is essentially then unprotected. Okay, let's now talk about muting and
30:39
mute inversions. So imagine you are using endpoint security and you go to create a file
30:47
monitor. Awesome. You subscribe to all the file events. You get the entitlement. You compile it. You run
30:53
your file monitor and you're immediately overwhelmed. Why? Two reasons. First,
30:58
there are a ton of legitimate file IO actions happening all over the system. And then secondly, if your tool actually
31:05
prints or writes to the terminal, that is going to generate file events itself. The endpoint security is going to
31:11
deliver back to you that then you're going to print out. You're going to kind of go into this recursive loop. So, what
31:17
we really want to do is tell endpoint security, okay, thank you for all the file events, but there's certain things that we want to avoid that we want to
31:23
ignore. For example, we want to ignore our self as the responsible process. Or
31:29
as we will see, you can also tell endpoint security to actually ignore or mute certain events. Perhaps you want to
31:35
ignore all file events that are destined for the temporary directory. You just
31:41
don't care about those. So let's start with talking about how to mute a process. Again, this is telling
31:47
endpoint security you are not interested in receiving any events from the specified process. You do that via the
31:53
aptly named ES mute process API. This takes an initialize client and then the
31:59
audit token of the process. So there's a snippet of code on the slide where we're going to mute ourselves because we don't
32:06
want uh file events from our own file monitor. That's pointless. Question though, how do you get an audit token?
32:12
And what even is an audit token? So an audit token is just a more modern way of
32:18
identifying a process. PIDs are reused which introduces a bunch of security issues. So audit tokens are a better
32:26
way. The problem is a lot of APIs still either want a PID or give you a PID. For
32:31
example, if you enumerate all the running processes. So you might be wondering how given a PID you can get
32:36
the processes audit token. Turns out you can use the task name for PID API.
32:42
Here's some example code that does that. Given a PID it will give you the audit token for that. Make sure though you
32:49
always call mockport deallocate otherwise you'll have a memory leak. Again found this out the hard way.
32:56
You can also mute the process via the esmute path API. Instead of a audit
33:02
token this takes a path. So again snippet of code on the slide we mute
33:07
ourselves by providing the path to our own process.
33:12
Okay. So that's how to mute processes. again telling endpoint security, yo, we don't care about any events for this
33:18
specific process. Well, what if you instead want to mute specific events? Like I mentioned, perhaps in your file
33:25
monitor, you want to ignore everything that is destined for the temporary directory.
33:30
Well, turns out you can do that as well. And the good news is you use actually use the same ES mute path API as its
33:38
last parameter. This API takes a type which tells endpoint security what what
33:44
thing you're actually trying to mute either a process or the actual event. And we can see on see on the slides
33:50
there's four different types in two categories. The first category tells it to mute a process. The second one tells
33:56
it to mute a path or an event. In each group there are two types.
34:02
There's ones that end in prefix and one that ends in literal. Literal just means you're going to give it the full path to
34:08
the process or the event. Prefix means it matches a prefix. So if we want to mute all file events going into the
34:14
temporary directory or any of its subdirectories, we use the target prefix type. One more nuance because endpoint
34:22
security is full of nuances. Endpoint security does not support or handle sim
34:28
links. So that means we can't actually just give it /tmptemp because on Mac OS that is sim linked.
34:35
The mute API will succeed but you'll actually still see events from /temp
34:40
because again it's sim linked and endpoint security doesn't support that. So you either has to resolve that path
34:45
yourself or dynamically look it up. All right let's now talk about mute
34:52
inversion. Conceptually this is pretty straightforward to explain the APIs is a little bit more complicated. It messes
34:58
with my head, but I'm going to try my best. So, so far we've been talking about endpoint security messages in a
35:05
very global context, right? We've talked about process monitors and file monitors that once we subscribe to these events,
35:12
endpoint security says, "Here are all the events. Here's all the processes. Here's all the files." And yes, we
35:18
showed how to mute a few of them. But what if we want to do the opposite? What if we want to do the invert?
35:24
Specifically, what if we want to write a file monitor to analyze a piece of malware and ignore every process except
35:32
the one specific one we are running the malware. We want to see how the malware persists, what files it generates. Well,
35:38
turns out you can now do this via via mute inversion. Another example, say you want to protect
35:45
the user's cookies or document directory. We have some source code from
35:50
Mac stealer. It's a malicious Python script and we can see it's accessing Google Chrome's cookie directory to grab
35:57
all the cookies. So what we could do is write a security tool that monitors this directory and only authorize for example
36:04
the browser. Again we don't care about any other directory. We only care about this specific one. This is something
36:11
that mute inversion can help us implement. So how does one actually utilize mute
36:18
inversion? And this is where it gets a little complicated, at least to me. So what Apple could have done is implement
36:24
new mute inversion APIs. For example, mute invert process, mute invert path.
36:29
But what Apple did which was very slick is they said, "Okay, you already have mute path and mute process APIs. So what
36:38
if we provide a new API that just toggles mute inversion and then you can still use those older APIs or the
36:44
original APIs but now they will be inverted. And so that's exactly what we
36:50
can do and I'll show some code that hopefully illustrates that a little better. So first we can invoke invoke
36:56
the ES invert muting API. This will unmute anything that's already muted but then mute everything else.
37:04
First though, we have to talk about some more nuances. Specifically, the default mute set. Turns out when endpoint
37:10
security starts, Apple, without really telling anybody too much about this, mutes a bunch of quote cit system
37:18
critical binaries that protect clients from panics and timeouts. So, a bunch of system processes are actually muted by
37:25
default. Well, this is problematic if we invert muting because remember when I said we invert muting that first unmutes
37:32
everything which means it's going to unmute the default set which is not what we want to do. Apple says okay if you're
37:38
going to do mute inversion make sure you call es unmute all first. This will
37:44
temporarily unmute the default set and then when you invert muting, which mutes
37:49
everything, it will mute the default set back. Essentially ensuring that the default mute set is always muted, which
37:56
is what we want. Let's now look at some code that implements mute inversion that hopefully
38:03
makes this all a little bit more clear. So here is some code to protect the user's directory. Specifically, we're
38:09
going to register for the Oop API event. This will be delivered to us anytime
38:15
anybody tries to open any files. In this case, in the users document directory.
38:21
Top part of the code, don't worry about it. In the bottom though is where we find the mute inversion logic. The first
38:26
thing we do is unmute all the paths. This is to handle the default mute set. We then invert muting. This remmutes the
38:33
default mute set and then also tells Apple when subsequently we call the original mute APIs instead of muting
38:41
things it should unmute something. So on line 19 we invoke esmute path but since
38:47
we've in muted inverted muting this will actually tell endpoint security that we
38:52
are just interested in events for the users document directory.
38:57
You can read more about that in the book. But if we compile this code and execute this, we can see now anytime a
39:03
process attempts to access the user's documents directory, we get a notification just for this. No other
39:09
files. We don't care about anything else. And if it's something like finder, we can trust and allow that. Whereas if
39:15
it's something like Mac stealer, we can block that and protect the user.
39:21
So that's mute and mute inversions. The next thing, one of the last things I want to talk about is what's new. I
39:28
mentioned that Apple continues to invest in endpoint security which is awesome and something I really appreciate.
39:36
And one of the great things they do is they often add new events. This is added in the ES types.h file.
39:43
You can open that and you can see towards the end of the big structure that contains all the events, the new
39:49
events that are added. Apple also adds comments explaining what versions of Mac
39:54
OS these new events are supported on. because here's another nuance. They don't backport them, which is fine, but
40:01
just something we need to be aware of. So, if we look at this enum, we can see
40:06
some of the latest events they've added, and they're actually super cool events. So, for example, in Mac OS 10.13, they
40:13
added the XP malware detected notification event. XP is XProtect. This
40:19
is Apple's internal Mac OS antiirus product. I don't know if we can quite determine it that, but it's a malware
40:25
detection capability. They've now added an endpoint security message that your tool can subscribe to that when Apple
40:32
detects some malware, it will let you know as well. Super cool. Another one is the BTM launch item ad. This is related
40:40
to persistence. If you register for this method or this event now, anytime anything persists on
40:48
the system as a login item, launch Damon or launch agent, Mac OS endpoint
40:53
security will let you know. This is super useful as well because the vast majority of malware persists in this
40:59
manner and now we have a generic way to detect that something was just persisted. Super cool. And then finally,
41:06
in Mac OS 15.4, Apple added the ability to see TCC events, which is amazing. I've been
41:12
begging for this for years. So, we'll look at this on the next slide. But before we jump to that, note that if you
41:18
want to use the new events, you should wrap them in some runtime safety checks again to ensure that if your tool is run
41:25
on an older version of Mac OS where these new events are not available, bad things don't happen. If you're using
41:31
Objective C, you can just use the available keyword and the compiler will take care of everything else.
41:38
So, let's briefly talk about this new TCC event because it's something I'm super stoked and really appreciated that
41:44
Apple added. So, many of you are probably familiar with TCC. Quick reminder, it is the technology on Mac OS
41:52
that protects sensitive user components and sensitive devices on Mac OS. If we
41:58
pull out extracted strings from the TCC Damon, we get a comprehensive list. It's it's things like your address book, your
42:05
calendar, your phone calls, your Face ID, your desktop, your photos, things that Apple rightfully says, "Hey, should
42:13
be protected." This is great because it means if malware even gets on your system, if it tries to access your photos or your location, TCC will block
42:20
that. Malware, though, is starting to catch on. And some of it has some samples
42:26
have, you know, exploits to get around this, but the run-of-the-mill malware just asks the users, especially if the
42:34
malware is in a Trojanized application that the user thinks is legitimate. So,
42:39
as an example, we have Gravity Rat. Gravity Rat can detect if an item it's interested in, for example, your photos
42:46
or documents are protected by TCC. And in that case, it just shows the user an
42:51
alert saying, "Hey, I can't run until you grant me full disk access." essentially sidest stepping TCC. And
42:59
again, since this is a Trojanized application, naive users might not think anything's a miss and then go ahead and
43:05
grant Gravity Rat or the terminal full disk access. Previously, security tools could not see this happening. However,
43:12
because of this new TCC modification event, we now can register for that and get alerted if the user or malware
43:20
modifies the TCC permissions. Now, the structure for this new event is
43:25
pretty involved and the documentation wasn't that good. So what I do in this case is just execute Apple's ESS ES
43:33
logger tool, specify the new event and then perform some action to trigger that
43:39
event and then look at what the values are reported. So if I follow the instructions for
43:46
gravity rat and go into the systems settings preference pane and give terminal full disk access this is what
43:54
ES logger will report to us for this new TCC modification event. We see the
43:59
responsible process is TCCD. This is not super useful. It's the same for all
44:04
these messages. Uh it's just because the TCC Damon is the one actually making the TCC modification. More importantly
44:11
though are the values in the actual event. We see the TCC access that was
44:16
granted in this case full disk access. We see the subject of permissions that
44:22
is the process that was granted the TCC permissions in this case the terminal. And then finally the instigator. This is
44:28
kind of like another responsible process. And in this case because we are following gravity rat instructions and
44:34
doing it via the system preferences application. That is the value of this instigator application.
44:40
We can then implement this in code. Again, this is just for a resource. But this is how to extract the relevant
44:46
members from that new TCC event. So you can take some action to decide if this is something that you want to block or
44:52
look into. You know, is it malware granting itself TCC permissions? Is it the user giving TCC permissions to
44:59
something it should not? Etc., etc.
45:04
Now, the last new thing I want to talk about that I'm really excited about, yes, I get excited about these things,
45:09
is new in Mac OS 26, and it is ESCS validation category. And what this is is
45:17
endpoint security will now for processes tell you the code sign validation
45:23
category. As we can see in the enum, the values for this range from platform, if it's a
45:29
platform binary, part of the operating system to development, app store
45:34
locally, if it's ad hoced and this is all super super cool. Why is this super super cool? Well, previously endpoint
45:41
security clients had to compute or figure out this information themselves. Why? Well, let's take block for example.
45:49
Blockblock treats applications from the Mac OS official app store differently
45:54
than ad hoc signed binaries. This is because apps from the uh legitimate official trusted Mac app store are
46:02
signed, validated by Apple and also run in a sandbox. So they can't really do much bad. So there's very few examples
46:09
of actually malware coming from the Mac App Store. However, there's a ton of malware that is ad hoc signed.
46:15
Previously, endpoint security would just tell you, hey, this process is signed and it would be up to you to determine
46:21
how it was signed, either ad hoc from the Mac App Store, etc., etc. Now, you could do this, but it was a little bit
46:28
complicated and used a lot of code and it was somewhat CPU inensive. Well, the great news is in Mac OS 26, endpoint
46:35
security will now tell you this. So, you can just delete all your old old code and your code is both now simplified and
46:42
more optimal. Hooray. All right, the last thing I want to talk
46:47
about are some limitations because at this point we've touched on a lot of advanced topics and hopefully
46:53
illustrated the power of endpoint security. So you might be thinking it's a panacea and it almost is save for two
47:00
main limitations. First, events sometimes aren't as comprehensive as we
47:05
would like. So for example, the TCC event that we just talked about is only delivered when TCC is modified. There's
47:12
a lot of malware that actually checks if it has TCC permissions that does not generate currently any ESS event. I
47:19
would like that because legitimate software often doesn't check these things. So, this would be a very good
47:25
thing to have. Also, if malware tries to perform some TCC action that's blocked,
47:31
that also doesn't generate an event because the TCC event is just for modifications. So, on the slide, we have
47:36
malware known as Windtail and Joker Spy. Joker Spy checks to see if it has TCC
47:42
permissions. This generates no endpoint security notifications. Wind tape tries to execute the screen capture utility to
47:49
take a screenshot. This is now blocked by TCC. Also, we don't get an endpoint security message for this. So, this is
47:56
just one example, but sometimes the events are not as comprehensive as you'd like. So, be aware of that limitation.
48:03
The other limitation is endpoint security events only trigger for new activity. This is not a critique of
48:08
endpoint security. It's just understanding what it is designed to do. So if you're writing a security tool and
48:14
you get installed on a new system, you might want to for example enumerate all existing persistent items or look at
48:21
everything that has already been granted TCC access. Endpoint security is not going to help you there. Neither should
48:27
it. So again, just be aware of that limitation. And then also endpoint security doesn't cover everything. So,
48:34
for example, if you want to do hostbased network monitoring, endpoint security does not provide information about
48:40
network uh activity. Instead, you're going to want to use Apple's network extension frameworks. Some resources on
48:46
those additional u technologies, but again, the takeaway here is you might need a supplement to create a
48:52
comprehensive Mac security tool. All right, finally, some conclusions and
48:59
takeaways. really two main takeaways that are pretty simple. First, endpoint security
49:04
should be your your bestie. I cannot tell you how amazing it is for using or
49:10
for creating uh security tools on Mac OS uh because it really gives us the ability to to uh uh detect or at least
49:18
observe essentially any action that even the most sophisticated malware performs.
49:24
Now, it's up to us to determine if that action is malicious or not. That could be a whole separate talk, but at least
49:29
provides us the ability to observe the events of even the most sophisticated threats.
49:35
Other takeaway, make sure you use the more advanced capabilities of endpoint security, caching, authorization events,
49:42
deadlines, etc., etc., but be aware of the nuances and limitations so you don't
49:48
get bit figuratively in the butt. Now, if you are interested in learning more, I already mentioned the Art of the
49:55
Mac Malware book series. I just want to reiterate that again because tomorrow I'm going to be doing a book signing at
50:00
No Starch Presses and we're actually going to be giving away I believe 20 or 30 copies for free. So if you want to
50:06
grab a copy, show up first come first serve. Uh so I can sign that. We can talk nerdy about endpoint security. Also
50:13
if you're interested in Mac security topics, Apple security topics, I want to invite you all to Objective by the Sea,
50:19
which is three days of dedicated Mac security talks from the world's top Mac security researchers. Also, I'm doing a
50:26
training there on this exact topic and lots more 3 days. So, if you want to learn more and get a little bit more
50:32
hands-on, check that out as well. Briefly, also want to mention the
50:38
Objective C Foundation. Uh we do a whole bunch of really cool stuff. So, if you're interested in learning more about
50:43
the conference, our student scholarships, and our diversity programs, check out objectivec.org.
50:49
Finally, I first and foremost want to thank y'all for attending my talk. Nothing worse than me as a speaker
50:55
giving a talk when no one shows up. That hasn't happened yet, but very thankful for you being here. Also then, round of
51:01
applause for Defcon. [Applause]
51:07
I run OBTS, so it would be kind of blasphemous to for me to say Defcon's the best conference, but kind of is. So,
51:14
shout out to that. And then finally, I just want to thank the friends of Objective C. These are the companies and
51:19
products that support the foundation, support my research, make us uh be able to give the books for free, etc., etc.
51:26
So, if you know anybody who works at these conf companies, give them a high five and thank them. So, that is a wrap.
51:33
Here are the resources. If you want to learn more again, thank you so much for attending my talk. Go out and write some
51:38
great security tools using Endpoint Security. Thank you.