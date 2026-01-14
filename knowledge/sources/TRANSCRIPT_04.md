0:00
Let's go back uh nine years ago to the summer of 2016. Uh it was about to be
0:06
just a regular summer, you know, going to the pool, attending Defcon. But little did we know, Niantic, a mobile
0:13
game company, was about to release um a new game called Pokémon Go, condemning
0:18
thousands of nerds to be collectively sunburnt. But jokes aside, this was a dream come
0:25
true for me and for many, you know, being outside chasing Pokemon, uh,
0:31
battling for gym access. It was really, really a dream come true. Uh, except it
0:37
wasn't so much for me. I lived in a rural town back then, and there weren't any Pokémon around me. Um, and while
0:44
everyone in the city was having fun, I had to chase down um, Pokémon very far
0:50
away from my home. And all I had uh, in fact was this lousy scanner. I don't
0:55
know if you remember it. Um, but you could only see the nine closest Pokémon
1:00
to your location and uh, a footprint one to two or three showing you how close
1:06
they are to your location. And honestly, this sucked and all the Pokémon were
1:11
rattatas anyway. Uh, these are real pictures of me with my friend. Uh, so
1:16
naturally, I decided to build a Pokemon scanner that would tell me where all the Pokemon are and those that I haven't
1:22
caught yet, so I can flex on my friends. Um, so little did I know this uh idea
1:29
would take me to an adventure uh of uncovering the Pokémon Go protocol,
1:34
understanding how it works, and also having to overcome very difficult defense mechanisms uh against uh fake
1:42
scanners. Hi everyone, my name is Tal. I know my last name is hard. Uh I'm a security
1:49
researcher by day and well a security researcher by night as well. During the day, I get paid to lead the research
1:55
team at ASIC Security, a cyber security startup uh doing identity security. And
2:01
by night, I do independent hacking, CTFs, and all sorts of crazy projects. You can read about in my blog. Um I
2:08
actually, it's not the first time on Defcon. You noticed I haven't done any shots. Uh in Defcon 31, I talked about a
2:15
zero day in GCP and I'm very very very excited to be here today. Thank you all for coming to hear me. Um
2:22
this talk will be accompanied by a two-part blog post that will be live on my blog right after this talk. It might
2:28
be even live right now. Uh so you are free to uh go and read it afterwards. I
2:33
go into details uh further than I am in this talk uh due to lack of time. Um I
2:39
also have uh quality stickers limited time edition that I will be giving away after the talk. So, feel free to come
2:46
by, ask me questions, take your sticker, and you can also reach out to me on social media. Uh, and like every good
2:52
Pokémon trainer, we need to collect badges. So, we'll collect six badges during this talk when we overcome a very
2:59
difficult gym battle. And you can use this to uh know where we are on the talk approximately. Um, one last thing, uh,
3:07
so this research was done independently 9 years ago. U most of the techniques that I'm going to show you today no
3:14
longer work on the actual app. Uh so this talk is mostly to to show you how
3:20
the mobile hacking game community uh looks like and I have references. So all
3:25
the uh images that I'm going to show you today are based on publicly available data. I will be sharing the references
3:32
slide uh at the last slide. Uh with that out of the way, let's begin.
3:37
So I hear you want to create a Pokemon scanner. Hello. So I hear you want to create a Pokemon scanner. Uh and we know
3:45
that the Pokemon Go app operates something like that. So uh it has to get the information that it displays in the
3:51
lousy scanner. All right. So it has to uh request data to get all the Pokemon
3:57
and get back all the nearby Pokemon uh to its location. And this is a request that I want to forge uh to say that I'm
4:04
in a different location and get all the Pokemon around that location. Um, but who's to say that the app doesn't get uh
4:12
only the uh information that is played on the lousy scanner, so only a list of nine Pokémon and the footprints of how
4:20
far they are from you. Uh well, there are two hints. one, if you play Pokémon Go, you know that once you're close
4:26
enough to the actual Pokemon, it immediately appears on your screen at a very specific location, which kind of
4:33
tells you that the app knows the the exact specific location. The second hint is that servers are lazy. So, no one
4:40
wants to do this heavy computation uh that has to do with determining how far a Pokémon is to you. Uh, and Niantic uh
4:49
would be happy to delegate this computation to your device. you have a very powerful Android device or Apple
4:54
device uh in your pocket that can do this calculation for you. So, I'm not sure that I convinced you, but I did
5:01
convince myself back then, and I'm happy that I did. Um, and I wanted to see how
5:06
the uh to to be able to do this request. I wanted to to see how the protocol
5:12
looks like. And to see the protocol, uh I have to uh look at the traffic that
5:17
goes between uh the Pokémon Go app and the Pokémon Go servo. And this is attack
5:22
called uh sniffing attack. Um we can pretty guess pretty much guess that the
5:28
app and the server communicates over HTTP which means that we need to employ
5:33
an HTTP proxy to look and record the information that goes back and forth. In
5:38
Android, that's pretty simple. You spin up an HTTP proxy on one of your machines. You go to your Wi-Fi settings.
5:45
uh you put the IP address of your machine in this proxy settings and immediately you start seeing traffic. Um
5:53
I used Fiddler Classic back then. I still use it today. Call me an oldie but I really like this program. And this is
5:59
how the real uh communication looks like in Fiddler. As we can see uh the app
6:05
starts by requesting a generic endpoint and then uh switches to a specific
6:11
endpoint probably for load balancing issues. Um and now we are able to see the communication between the app and
6:17
the server. And for this we get our first badge, the badge of sniffing. Um
6:23
okay, we have the communication. Let's dig deep into the actual protocol. So as
6:29
you can see here, we can see that the uh request content type that is reported um
6:34
by the app uh is actually form URL and encoded. as as you can see it is lying
6:40
because if you ever saw form URL and encoded it's textual protocol and here uh the protocol is clearly binary um so
6:48
what's going on let's look a bit deeper into the actual uh binary of the of the
6:53
request on the left maybe it's on yeah it's on the left for you on you can see the bytes being sent on the wire and on
7:00
the right you can see the ask representation of them when it is possible uh and it probably means nothing to you but luckily at the time I
7:07
happened to look at this exact scenario multiple times. So I immediately noticed some very telling clues here. The first
7:14
one is that the first bite of the request is 08. Uh and the second is that there are some glimpses of readable text
7:21
which mean that this not encrypted but rather serialized and I immediately realized that this is protobuff.
7:28
Protobuff is short for protocol buffers. This is a very well-known framework uh
7:33
developed by Google and maintained by Google uh that uh takes very complex objects and knows how to dis to
7:40
serialize them. So two separate systems like an Android app and a server can
7:45
communicate with each other even though the objects are can be relatively difficult. So let's take a second and
7:52
switch the screen to this very very uh nice uh pink hue uh to talk about proto
7:58
protobuff. So as a developer you define uh a portabuff message which is the
8:03
object you're going to send and the definition looks something like that. So this is just an example definition uh
8:08
from the portbuff documentation. Uh we define a search request message. It has four fields. The first field is a query
8:14
of type string. The second field is a page number of type integer. And then there are actually two optional fields
8:21
that don't have to appear in every object. And as you can see the fourth field actually the search options is a
8:27
repeated field which means that it can it can appear more than once kind of like a list. Uh as you can see its type
8:34
is a search option. So you can embed messages within other messages. Uh and we don't have a declaration of a search
8:40
option here and that's on purpose. Uh and to use it you use um a tool uh as I
8:47
said developed by Google named protoc. You take this definition, you kind of compile it into your favorite language.
8:54
Uh for this example, I compiled it into Python and then you can simply import uh
9:00
the resulting file as you can see here. Um on on the left uh this short code
9:06
imports this library, creates a new self set request object, fills it with
9:12
information, serializes it, and send it on the wire. Good. So we know now about protobuff uh
9:20
but we have a problem. We see the serialized data on the wire but we don't have the original definitions. So what
9:27
we can do about that? Luckily protoc supports a flag named decode raw. It's
9:32
the best flag ever which basically tells protocalize this message without having access to
9:39
the actual definitions. If we would we would take the message that I created here that was sent on the wire and
9:46
decode it uh use the decod raw flag on it we' get something like that. So as you can see uh it's not looking like the
9:54
original. We don't have the field names. Uh maybe some of the uh types are wrong but we can okay um but we can still uh
10:04
learn a lot about uh the underlying definition just from seeing the decalized uh message without the
10:10
declaration. Uh and we can even tell some some things about the message that we didn't see the declaration of. Right?
10:16
You can see that it has two fields. Both of them are strings. Uh so let's apply this technique to the actual message
10:23
that we just saw for Pokémon Go. So here it is. It's very loud. You probably can't see anything, but that's fine. Um
10:29
and um so at first this looks a bit this might look a bit difficult to
10:35
understand. And today you have tools like PBTK that basically goes and look
10:40
at the binary of like an Android app and extract all the definitions all the compile definitions from it. Back then
10:47
understanding proto definitions was nothing short of an art. Um, and I use several techniques uh to understand how
10:55
messages look like and how the protocol works. Uh, I go uh deeper into them in my blog post, but here I'll just cover
11:02
the three main uh tips and tricks that I used. Uh the first one is you can tell a lot about fields using their value. So
11:08
if you have um very clear values like the strings at the bottom there uh that
11:14
you can immediately if you know this you know that this is an open ID token uh then maybe uh field 10 is an
11:20
authentication field. Um the second uh trick is actually knowing that some of
11:25
the different types like hexacode and integers that you can see there and floats share the same uh code. So
11:33
sometimes protoc C when it tries to decode them, it doesn't know what's the original type is so it just tries its
11:39
best. And if you would go and convert those uh x- encoded integers into
11:44
floats, you would just see that they are a coordinate. So this is my location. Um
11:49
and the third technique is actually uh by interacting differently with the app like making a different action or moving
11:55
to a new location. I can see the messages that are are changing slightly and using these changes I can infer a
12:02
lot of uh information about the underlying declaration. I will save you all of that. You're welcome to go to the
12:07
blog to read more. But after understanding some of the fields of the request, I ended up with this
12:14
declaration which is a bit shorter so you can see it better. Uh so how
12:19
requests looks like from the Pokémon Go app. Uh so it's actually I called it a request container because it contains
12:25
requests. Uh the request container has some metadata fields like the request ID uh my location, my authentication info.
12:33
Uh and it has a repeated field that I named requests. Uh that uh uh includes
12:39
um all the different requests that the app wants the server to answer on. Each request has a request type and
12:46
optionally request by if uh it needs to. So here it sends uh three different
12:51
requests 106, 126 and four. Um and the server response looks relatively the
12:58
same. So it has a response container this with the same request ID and a repeated response field. Uh each
13:04
response corresponding to one request. So it's always matching one to one according to the same order.
13:11
Okay. So now that we know how the general format looks like, uh we have to try and find the actual request that
13:17
gets the list of Pokémon, right? That's what we wanted to do for the for the scanner. Uh, but there are tons of
13:23
different stuff, ton of different types of requests and I tried to do a few things like searching for Pokemon names,
13:29
searching for locations around me. Uh, but I didn't really manage to find the actual uh request type that I wanted.
13:35
And what actually solved it for me is playing Pokemon. So, if you played Pokémon, you know that all of them are
13:41
indexed by an incrementing number. Um, and by looking at the lousy scanner and seeing that it scanned uh a PG and a
13:48
rada, I searched for the number 16 and 19 and I found a hit. So, turns out
13:54
request number 106, which was later uh was changed to name uh get map object.
14:00
That's that's the title um is a request that uh takes as input an identifier of
14:06
a cell and as a response uh looks something like that. uh it responds with
14:11
a map cell object uh that basically uh includes all the different objects that
14:16
are on the this specific map cell in the area including forts which is the internal name for gyms, poker stops uh
14:24
etc. It also includes spawn points and Pokémon and more importantly uh it has
14:29
the exact location of the specific Pokemon in this map cell. As you can see, there is a catchable Pokemon at a
14:36
very specific location. Uh, and this is the Pokemon number 23. So, who is that
14:41
Pokémon? I hope you know it. Um, so upon successfully understanding the protocol
14:48
of how the Pokémon Go app uh requests and gets all the Pokemon in a specific location, we earn our second badge, the
14:56
Bradger Protocol. All right. So, uh what do we know so far? uh we know that uh
15:03
the the communication the protocol uses protobuff and the main message that is being sent is a request container. It
15:10
contains some metadata uh uh on the request uh including a list of requests,
15:15
one of which is request number 106 that fetches the map details for a specific
15:20
cell. It gets a cell ID and responds with the exact location of Pokémon which is the best case scenario uh for a for
15:28
building a scanner. uh but we still have three open questions. So the first one is how do you construct a request
15:34
container? So it has complicated fields authentic like authentication fields. How do you do you create them
15:40
successfully? Uh second there are still plenty of fields and request type that I just didn't know. So I call them unknown
15:47
like unknown six. Um so do I need to create them in order to
15:52
make a successful request? I don't know what they're used for. And lastly, what the hell is a cell ID? I'm used to
15:59
coordinates. I don't know anything about cells. So, turns out the answer to the first two questions was actually pretty
16:05
simple. The server just doesn't care. Uh it was very very lax regarding what the
16:10
data that it expects in a request container. You basically only had to send a request identifier, your
16:15
authentication info, which is very straightforward, and a single request 106 uh with your cell ID. It didn't care
16:23
about other fields that I understood. It didn't care about all the fields that I didn't understand. It didn't care about
16:29
other request types. So, best case scenario for me h about that cell ID. So, keen eyed of you may have noticed
16:36
that in the previous slide, I call this an S2 cell ID. Turns out uh Pokémon Go
16:41
uses a framework named S2 cells. It splits a sphere, in this case the Earth,
16:47
into cells. Uh you decide on a level which basically controls the size of a specific cell. Pokémon Go works with at
16:54
least get map object works with level 15. Um, and then you have a very very
16:59
simple uh calculation. There's very a lot of calculators online that take uh a
17:04
specific coordinate on Earth and converts it to a 64-bit cell identifier that you put um excuse me uh in your uh
17:13
GitLap request uh uh as the the cell that you want to to find Pokemon on. So
17:21
with all the question answered uh I went and created a Pokemon scanner. This is my code from back there. Uh a very nice
17:28
code. I'm sure you can you can see for yourself. Um it uh gets authentication
17:34
in from Google. It contract constructs a request container with this authentication info request identifier.
17:39
It adds uh so it starts on with a specific location basically all around me. I scan like a radius of of a few
17:47
miles. Um, and for each location, it adds a new get map object uh request.
17:53
Uh, converts my uh the the actual coordinate to an S2 cell, gets the
17:58
request, passes the respond, puts all the different Pokémon that finds on a map, and we have a request container.
18:05
Um, and dumb me. I didn't really record any of the actual uh uh maps that I
18:12
built uh with Pokemon from back there. I only actually had this one picture of a log uh that I had and you can tell that
18:19
it's not fake and real because I had to blur out my actual location. Uh so that's my only proof to you. Uh but this
18:26
is an example log from the scanner that it searches for different Pokémons. I think here it found a Pidgey. Um and it
18:33
was great. I spent I flexed on all my friends. I found all the cool Pokémon. I I used it for a couple of of of weeks.
18:39
Uh, and upon successfully creating a a Pokemon scanner, uh, we get our third badge, the badge of Pokemon.
18:47
So, uh, one quiet Wednesday, I went I got back home and I started my Pokemon
18:53
scanner to play a nice, uh, evening of Pokémon Go, uh, only to discover that it
18:58
didn't work. Um, and so my scanner got like a generic error, uh, that I really
19:04
didn't understand. So naturally, I opened up Fiddler, my HTTP proxy, to see how the information, how the protocol
19:10
looks like. I knew that a few days earlier uh a new update was pushed to the app. Maybe something some stuff in
19:18
the protocol has changed and I needed to update my my scanner. Uh and the fiddler
19:24
didn't record anything. And in fact, while it was open, the Pokémon Go app refused to to turn on and refuse to do
19:32
anything. Um, so okay, we have a challenge. We have a fighter on hands.
19:38
Um, so naturally I went online uh to search if anyone else has encountered
19:43
this problem. And I realized that I wasn't the only smart guy in the room that decided to build their own Pokémon
19:49
scanner. There were actually uh many different communities online uh uh doing this stuff. One in particular was
19:57
Pogdev, a community dedicated to creating unofficial API for Pokémon Go.
20:02
um they had noticed this uh uh issue as well and started tackling it. Uh and in
20:08
fact I found uh that their administrator had actually put up a Reddit post uh saying well we
20:15
know we know our API is down uh something has changed in the app. We've created a discord server to coordinate
20:22
efforts around this. So naturally I went on a discord server. I joined the internal hacking channel uh and we
20:29
started working towards solving this. Little did they know this step who would be uh the first uh out of a three-day
20:37
hackathon where I barely slept uh in which we try to uh overcome all the defenses that were put uh by Niantic
20:44
against unofficial API calls. Uh I will make sure to uh and we use various
20:50
techniques to overcome these issues. I will make sure to stop when I introduce a new technique. I will name it. I will
20:56
explain how it works and then we can see how we used it to overcome the defenses. Uh at uh on top of the of the title you
21:03
can see uh the timeline. So this started around 1:00 a.m. uh in the first day. Uh so you can follow along how long it took
21:10
us uh uh to do every step. So uh the first hurdle was the fact that
21:16
no one was able to uh sniff the traffic and see uh the protocol and how it looks like. Um, and we thought uh and and
21:25
actually one researcher uh found this interesting uh uh class was added to the
21:30
Pokémon Go app named Niantic Trust Manager. Uh and uh so it implemented a
21:36
check server uh trusted function uh which seems like it implements a defense
21:41
called uh certificate pinning. Um and to understand how we overcome it, we first need to understand uh why it works
21:48
against uh HTTP proxies and basically blocks their behavior. We need to talk a little bit about HTTP proxy. So here you
21:55
can see a very very high level uh overview of how HTTP proxy works courtesy of CHGP. Um basically uh
22:04
normally when you work with HTTPS uh the client communicates with the server in an encrypted form. That's what the S
22:10
stands for, secure uh based on a certificate that is provided to the server uh to the client. Uh and besides
22:18
confidentiality, uh HTTPS also promises you integrity, which means that you know that you are talking to the real domain
22:24
and not a fake domain that says, "Hey, I am a Pokémon Go server." Uh but that's
22:30
exactly what HTTP proxy needs to do. it needs to convince the client to speak to it and it will uh parse and and and
22:38
decrypt all the communication, log it and then pass it on to the server. So it works because you own the client. The
22:44
HTTP proxy generates a certificate that you install as a certificate authority
22:49
on your client which basically allows the HTTP proxy to create and sign any certificate that it wants for any domain
22:56
that it wants uh and convince the client that it is talking with the real server. This is how the uh certificate of filler
23:02
looks like on my Windows machine. It works the same way for Android. I just I was too lazy to pull it up from my
23:08
machine. Um okay. So now we understand how this works. So how do uh certificate
23:14
pinning works? By by doing certificate pinning basically the developer takes the public key of the actual server that
23:20
it intends to talk to and simply hardcodes it hardcode it uh into the
23:26
application. And what the application does it once a new session of HTTPS starts it verifies that the public key
23:33
of the server matches the public key that is embedded in the code. Obviously since the HTTP proxy generates a new
23:39
certificate the public key would be different from the real uh from the real deal. Uh and that way the client can
23:45
detect that it is actually interacting with the HTTP proxy and not the actual server and basically block the
23:50
communication. So how do we overcome it? we have to use a new technique uh uh that I call dynamic reverse engineering.
23:57
So we have to learn it um and h so what dynamic reverse engineering means is
24:03
intervening in the uh running code of an application and basically changing stuff
24:09
on the way. You can think about it similarly to developing code uh and debugging it and changing values while
24:15
it is debugging only automatically. Uh and there are a few frameworks that allows you to do it uh for Android in
24:22
particular. one of which is exposed which basically allows you to hook uh any Java class function that you want
24:28
and run code before it starts and after it returns. So we wrote this short
24:33
expose model. This is actually very short. I just uh removed the original change because it is very long. uh we
24:40
hook on the checked uh uh server trusted function of the Niantic trust manager
24:45
which by the way we found because it extends a very well-known class for certificate pinning named uh x509
24:53
uh trust manager uh that's a good way to find certificate pinning if you ever uh want to do so um we took the original
25:00
chain from the actual server this is public it's very easy to get and what we do is that that we hooked on we we did a
25:06
before hook so before the uh a function is called. So every time that is called we basically replace with the first
25:12
argument which is the certificate to validate with a real certificate. So that way uh the app always think that
25:18
inter it interacts with the actual server even though uh it is not. Uh so we full it uh that way once we were so
25:26
this allowed us to uh uh see the traffic again and what we saw kind of surprised
25:32
us. We saw that nothing changed. So all the protocol looked exactly the same as it as it was before. Um
25:39
so what was the problem? Um we realized that one what what might have changed is
25:46
one of the fields that was previously unneeded and optional started become required and the server started
25:52
verifying it. Uh and we needed to find it and there were various uh different fields that we didn't know various types
25:59
of requests that we didn't know. Uh so to figure out a specific field we had to
26:04
use a second technique that I call active probing. with active probing and actually used it a little bit for my
26:10
scanner. Uh you take uh a valid request and you start changing values with it uh
26:16
and sending it to the server until the server starts responding with an error. So what we did is we basically started
26:21
removing fields that were we knew were optional one by one until the server returned an error. And that way we
26:28
actually found a specific field uh the six field of the request container uh
26:33
became required which it was optional before. Um and so we did know a bit about the
26:42
format of the six field. We called it unknown unknown 6. Uh we knew that it
26:48
contained uh a message within and within a message there's a bite array and the bite array actually contains the
26:53
information within unknown 6. uh and we turned our sole focus of this research
26:58
was turned into unknown 6 uh which naturally uh it was natural to take the
27:03
name of it as the name of our group. So we called ourself team Ankown 6 uh and
27:09
we focused on cracking this. Um so starting off we wanted to know more
27:14
about anon 6 and how it looks like and to do this we'll use our third third technique which is kind of like the
27:20
counterpart to the active probing. I call this passive analysis. In passive analysis, it was also used for the
27:25
Pokemon scanner. Uh you generate a lot of different uh requests by interacting differently with the app or doing
27:31
different actions or simply generating a lot of different requests from a lot of different devices. Looking at all these
27:37
requests, you can infer a lot of details about how the protocol works. So what we did, we generated a bunch of of unknown
27:45
six example. This is one specific examples. As you can see, most of the information is within uh the one field
27:51
over there. I just I'll just call this unknown six for short. Um, and we noticed something something peculiar
27:57
from all of these uh samples. The size of uh this unknown 6. Uh, so it turned
28:04
out that the size of this was always a multiple of 256, one of my favorite
28:09
numbers, plus 32. So the size of this is just uh one block of 256 and 32. So 288
28:18
uh total. Um, another uh very nice uh
28:24
finding that one of the researchers did is that they set the time the clock on their machine to the exact same second
28:30
every time. And he noticed that all of the samples of Anon 6 that he generated began with the same 32 bytes. So we
28:38
managed to figure out that the first 32 bytes of uh Anon 6 uh only depend on
28:44
time whereas the rest depends on other things. Actually by doing active probing and taking a valid unknown 6 and
28:51
changing the request just the cell id in a getmap object request we also uh have
28:56
the server return an error which means that uh this unknown 6 is strongly tied
29:02
to the request we make. In fact the existence of numbers like 256 and the involvement of time we kind of guess
29:08
that this is some encrypted uh signature over the request that we make that now the server started to validate. It was
29:15
always sent to the server. it just didn't validate it before probably because they suffered from a lot of uh
29:21
technical difficulties in the first weeks of Pokémon Go due to the large number of of people that were playing.
29:27
Okay, so the next uh step that we wanted to do is to find where this Anon 6 is generated in the code so we can
29:33
understand what happens and how the encryption works and how the signature looks like. Um and we knew that
29:39
everything that has to do with protobuff is actually in the native part of the application.
29:44
So let me stop for a second. I speak a lot about the Java part of the application and the native part of the
29:49
application. So let me explain. Uh an Android application basically split into two parts. There's the Java part. It's
29:55
the more high level part that has to do with interacting with the Android framework and interacting with the user.
30:00
Uh and then there's the native part usually coded in C or C++ that is actually compiled and inserted as a
30:06
library uh that the Java part can call using NDK. Uh this is an interface
30:12
between them. actually the certificate pinning uh called it was a Java class that was calling a native part and
30:18
usually the native native code is used for more computational heavy uh operations and it's no wonder that
30:24
mobile games uh mostly rely on native code because they have a lot of graphical related computations
30:30
specifically Pokémon Go I think relies on Unity um okay so uh what do you do with uh the
30:38
Java part and the native part to understand it further you have to use our fourth and final technique which I
30:43
call static reverse engineering kind of like the analog to uh to uh the other
30:48
way around of dynamic reverse engineering. Uh you use specialized programs to inspect uh the actual code
30:54
that is being executed by either the Java part or uh the native part and use
31:00
specialized programs to do so. Uh these programs basically do the other way around. They start from an assembly,
31:06
they disassemble it back to their assembly assembly language. uh and then they also try to decompile it to uh get
31:13
as close as they can to the original source code that generated the app. Um with Java uh we have Jadex. It's an open
31:21
source tool. It's an amazing tool. It does an excellent job. Here you can see the Pokémon Go app opened in Jadex. Uh
31:27
and actually the the image from for from before of the certificate pinning class was actually from Jadex as well. It does
31:34
an excellent job reflecting back the bite code of Java uh into uh and the
31:39
actual code as close as possible to the original. Uh and it's relatively easy because Java is only uh compiled into an
31:46
intermediate language. Uh when it comes to native code, this is a bit harder and you have to use different tools. Uh this
31:52
is an example from IDA. Today we have Gedra which is also a great tool. Um they basically show you the actual
31:58
assembly. Um on the left there you can see the graph view of a function in IDA
32:04
and on the right you can see IDA trying its best uh to decompile the the assembly code back into uh C code. And
32:12
these programs what they actually allow you to do is to uh change the names of functions of variables, change the types
32:18
that are being used, define structures really to help you to understand difficult patches of code and uh get to
32:25
the point where uh the code that you're looking at is very close to the original code that was being developed.
32:32
So we knew as I said we knew that everything related to protobuffath including creation of unknown 6 is in
32:37
the native part uh specifically in a library named libniantic uh manager. So
32:42
uh so we opened it in IDA and we had to pinpoint the actual function that generates unknown 6 and there were a few
32:50
methods to do it. I I think I lay down three different methods in my blog here. I will only share one method uh due to
32:56
lack of time. uh this was the method that I used. If you recall uh using uh
33:02
um static analysis uh we uh sorry passive analysis we found
33:08
that the that the starting byes of the unknown 6 message are only dependent on time. So uh naturally the code that
33:15
generates unknown 6 has to rely on time somehow and once you have a binary library uh that relies on a system
33:22
function like time it needs to import it usually if it's not compiled statically. Uh so I went to IDA to the import table
33:29
and I did find the time function being imported and I looked at all the cross references meaning all the locations in
33:36
the assembly in the library that calls time. I found two. The bottom one uh wasn't related at all. It was very easy
33:43
to see the top one the function at offset 87444. I can't even see remember it. Um so the
33:51
once you look at the coder you see that the output of the time function gets fed into srand which sets the seed of all
33:58
the randomness that is going to come. Then this function generates 32 random bytes. And finally we could you could
34:06
see a lot of places in the code where the number 256 as a constant appears which really uh makes us makes us makes
34:13
us believe that we found the actual code that generates anon six and for this we get our fourth badge badge of anon six.
34:20
Um okay. So uh at this point we looked at a specific function uh that we
34:26
pinpointed. We called it sing encrypt function because we believe that it encrypts a signature. It was only
34:32
natural. Uh and uh we decided to verify beyond doubt that it's exactly the
34:38
function uh that we wanted to generate unknown 6. So we used uh active probing
34:43
again to excuse me dynamic reverse engineering again to detect that. Uh this time instead of exposed we use IDA
34:50
uh Freda. Freda uh is a very very powerful tool that allows you to uh
34:55
basically hook uh using JavaScript any function that you want. It works on Windows, Linux, Android. Um is very
35:02
strong for Android. Here you can see a short free script that basically finds the so it hooks on the native library.
35:09
It finds the actual address of the function that we want at offset 87444. It hooks both the enter of the function.
35:16
So every time it runs and the return uh and simply dumps the input and the output and by matching the output that
35:24
uh uh this hook uh recorded to the value that was actually being sent by the app
35:29
afterwards in our HTTP proxy we notice that it it is exact same value meaning that we did find the actual function.
35:37
Another uh better finding that uh uh we managed to do with this hook function is
35:43
actually look at the input to the encryption function which is our signature and we found that it is
35:48
actually portable again. So I heard you like portabuff uh and it's a very very
35:54
long uh uh object uh and there are some uh interesting uh strings there like
36:00
oneplus that was my device back then um and it looked like field that was supposed to be in the signature. So we
36:07
had that but before uh moving on we focused on the sig encrypt function in
36:12
trying to understand how does it manipulate this input to get to the encrypted output that we know and it
36:18
turned out to be quite simple. So I will be able to show you this this today. Here you can see the uh decompiled
36:24
version of the sig encrypt function. Uh uh and let's start with an input of length 700. I split it into 256 chunks.
36:33
the less chunks is a shorter one uh just for easier understanding. Uh so as we
36:38
knew it starts by calling time fitting it into srand and then generating 32 bytes uh for the seed which it uh
36:46
prepends to the beginning. So that's the 32 bytes that we saw uh in the final version. Uh then it pads the input to
36:54
the next closest uh block of 256 and actually the last bite is the remainder.
36:59
So the server knows how many bytes it needs to strip uh to get to the actual input. And this is not the interesting
37:05
part. This is the interesting part. We have encryption. So we have encryption at off offset 9D8.
37:12
Uh this is the encryption function. And first the function starts by expanding uh the seed into a block of 256 using a
37:21
known expansion mechanism and then encryption walks. So uh this expanded uh
37:27
SID is actually uses the in initialization vector to the encryption function together with the first block
37:34
to output the first encrypted block. It gets overridden to the first block which
37:39
is used as the IV uh with the second block to get the encrypted second block
37:45
and same way for the third block until we have our encrypted uh value that is
37:50
being used in unknown six. Uh and this is nothing proprietary. This is a very known well-known cryptographic scheme
37:56
named CBC mode. Uh that has to do with encrypting blocks based on initial init
38:01
initialization vector. So now that we know how the sing encrypt function works uh we split into two groups. One group
38:08
focused on encryption 9 whatever to understand how encryption works and basically replicate it. So we can
38:13
encrypt our own values uh because we want to encrypt our own signatures. The second group I was a part of actually
38:20
focused on the signature to understand how it is constructed. So we we can create our fake signatures uh to sign.
38:27
Um and actually I think it was five uh hours later the first group already
38:32
succeeded. They were very very good uh and replicating and getting the encryption to work. So how did they do
38:38
it? Uh they were very smart and they walked through the entire call chain of
38:44
the encryption whatever numbers that came afterwards. uh which means all the functions that could be theoretically
38:51
called by following the chain of calls from this function they automatically used IDA to decompile them into very
38:58
ugly C codes but it was a C code that compiles and execute exactly the same as the original assembly and they put them
39:05
all in a single C file which turned out to be of size uh 14 14,000 lines which
39:12
actually with a few fixes compiled successfully and allowed us to encrypt any input that we want too. Uh which was
39:18
a very good job by them. Uh and on for successfully replicating the encryption
39:24
function, we get our fifth badge, the badge of encryption. Yeah. Um so
39:30
meanwhile, the second group uh that I was part of actually uh focused on uh
39:36
understanding how the signature works. So there are few sub fields within the signature message that were very uh easy
39:43
to understand according to the values in the fields and you saw them earlier. So one was was one contained a GPS
39:51
information basically a dump of all the GPS information that you can infer uh that the device can get uh which called
39:57
location fix and the second one called device info contained a lot of different properties and string about our device.
40:04
Um and actually the third message that we found uh we understood uh what it
40:09
means uh quite finally. So people starting to generate a lot of samples of the signature that we started using
40:15
emulators and we noticed that this field was always empty in emulators and and and always filled with regular devices.
40:22
Uh so we understood that it contains sensor information. Obviously emulators don't have any sensor information. Real
40:29
devices does. Um it contains a lot of information regarding uh acceleration,
40:34
altitude, gravity etc. Um and actually uh uh at this point so this is how the
40:42
signature uh uh declaration looked like at the time what we understood so far
40:48
and and inclusion of fields like this field like the sensor info field. Um
40:54
actually something uh before that uh so people that were using active probing to understand things about the signature uh
41:01
uh protobuff uh started getting their account banned. Uh and this together with the existence of fields like sensor
41:08
information fueled the fears in the community uh that Niantic was using uh
41:13
the information within the signature uh to detect unofficial uh API usage. And
41:18
if you consider things like sensory info, this is kind of akin to tracking your mouse movement uh for captures. Uh
41:25
this is a data that is very hard to forge and we really didn't know how we are going to uh create this for fake
41:32
signatures. Uh but this thought also made us wonder does the server actually
41:38
verifies this? So to verify things like sensor information based on previous sensor information is a very very
41:45
difficult computational job and we know we knew that the servers were were under high load at the time. So we thought
41:52
well maybe not all fields in the signature are necessary. So we employed
41:58
active probing again using uh dynamic reverse engineering using Freda. We started removing fields from the
42:04
signature before it was encrypted and seeing when the server starts responding with an error and we found out that most
42:11
of the signature was not needed. So all the fields that you can see that are marked with not required were not
42:17
required. Uh and actually only six fields were required. All of these highlighted here two of which were just
42:23
regular time stamps uh which were very simple. So we we were left with just four fields to go. uh field 10, Phil 20,
42:31
Phil 22 and Phil 24. Uh at this point I recall uh the discord was going crazy.
42:37
So here we are at the at the end of the second day of the hackathon. We were very tired at the time. Uh and actually
42:45
uh we had to go to Discord and ask them to increase the limit of our server side
42:50
on our server size because so many people had joined and back then uh it wasn't so common for servers to grow
42:56
grow beyond 10,000 members in such a short time. And another thing that happened so we had this channel named
43:03
Research which all the hackers were a part of. uh and eventually because people who kept asking uh it was open to
43:10
the public but only for view not for chatting so only we were able to chat and it I remember that uh we had a voice
43:16
chat with like hundreds of people within it waiting and analyzing every message that we sent in the research. It was a
43:23
very uh humbling experience I can say. Uh but it was it was very very crazy. Uh
43:29
so going back to the fields that we wanted to figure out, we actually found that two fields field 10 and field 20
43:34
were generated based uh on the same function um which takes as input a
43:40
32-bit number a a byte array a string and outputs a 32 uh bit integer as well
43:47
which kind of looks like a hashing function. Uh and we found that field 20 was a very simple hash of this number.
43:56
We don't know what it means to this day. If you know, please approach me. I would be happy to know. Uh and the string of
44:03
your location uh chain together. Uh and this the output of the function was
44:09
inserted into field 20. Field 10 was a bit more complicated but not so much. So first you hash your authentication info
44:16
straight from the request container. Uh and then you feed the output of this hash as the integer to the second hash
44:22
of your location. And so we have two ashes uh both on the location of the of the user one of which is also on the
44:28
dedication info. Um so at this point we try to understand
44:33
what's the hash and one technique to do it is to look at the constants being used in the hash and comparing them to known hashes. Using this we very easily
44:40
found that it's a very famous hash named xx hash h and this was the 32-bit version of it. We also found a 64-bit
44:46
bit version of it and it was actually used for field 24. So field 24 was a repeated field a list as you can see
44:53
from from this uh and actually every request that was sent uh took the request bytes of the request and hash
45:00
them together with the same integer that I don't know uh and it was the hashing
45:06
the hash was added to field 24 so field 24 contained as many hashes as you had request so for this example you had
45:12
three hashes in field 24 and then we had the last field the final field uh the toughest nut to crack we actually went
45:19
in the wrong direction for a while because we saw that it changes frequently uh when your authentication info uh changes um uh but uh it turned
45:28
out to be completely false when one researcher found that the function that generates uh this field um didn't get
45:34
any input. So uh we this field could be basically anything. Uh and once we tried
45:41
to do it uh we at uh 7:00 p.m. at the third day 67 hours after the hackathon
45:47
started uh we finally managed to make our first successful API request and for this we get our final badge the badge of
45:54
API. Um thank you. I'll just take one
45:59
minute one minute to talk about so I was very interested to So this is my code from back there that implements the uh
46:06
the actual authentication. You can laugh at it while I while I talk for the last minute. Um I was kind of interested to
46:12
know what happened afterwards. So it turned out that so we all treated this effort as something that is necessary to
46:18
create a community driving community uh developing tools for for Pokémon Go. We really believe that having access to
46:25
this kind of tool makes make it possible for people that couldn't play the game normally to have access to it. Um and I
46:32
was interested to know where the Pokémon Go hacking scene went from this. So I kind of didn't get involved uh into more
46:38
stuff afterwards. So PCODev continued maintaining the API for about a year and
46:43
a half after this after which they stopped. Uh today I search online. There's also a couple bots that are
46:49
offered for cache uh with together with some unlocked versions of the app. I wouldn't install those. Uh which is a
46:56
file from what could have been if Niantic would publish an official API. Uh I'll skip this and I would just like
47:03
to thank uh both the team and on 8. They were amazing guys. uh I had fun to work
47:08
with them. I would also like EFF for supporting me and consuling me on giving this talk today. If not for them, I was
47:14
not here. I will also thank you for coming. Uh and there's a reference slide. Feel free to come grab some
47:21
stickers. Thank you for listening.