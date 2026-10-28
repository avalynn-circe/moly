# The three-question method

An error message exists for one reason: a person or a program asked for something, did not get it, and now has to decide what to do. The message is the only thing the asker has. It owes them three answers.

## What happened?

The event, in the asker's terms. Not the mechanism. The asker asked to save a draft, fetch a forecast, deploy a service. Say which of those did not happen. "Could not save the draft" is an event. "NullReferenceException" is where the code was standing when it happened, and belongs in the log.

Test: could the reader repeat this sentence to a colleague and have the colleague know what they were trying to do?

## Why?

The cause, or the rule that was broken, with the value that broke it. The code knew. It applied a rule, received a status, caught an exception, hit a limit. Carry that knowledge into the sentence. "The disk is full." "State code must be two letters; got 'minn'." "api.weather.gov timed out after 30 s."

When the cause is unknown, say that it is unknown and where the detail went: "An error this program could not classify. The detail is in the log under id x-41a7."

Test: does the sentence contain the value or the rule, beyond the verdict?

## What next?

One step the reader can take from where they stand. From where they stand: a user cannot read server logs; an operator cannot change the code; a model cannot open a ticket. The step is the reason the message exists. If the step is to wait, say how long. If the step is to tell someone, say whom, and give them an id to quote.

Test: after reading the message, could the reader do something in the next ten seconds that moves them forward?

## Putting it together

The form that answers all three in one breath:

> Could not `<what the reader asked for>`: `<cause or rule, with the value>`. `<Imperative step>`.

Three examples from the rules' own fixtures:

- Could not fetch alerts for MN: api.weather.gov timed out after 30 s. Retry in a minute.
- State code must be two letters, like MN. Got 'minn'.
- Upload failed: the file is 52 MB and uploads stop at 25 MB. Compress it or split it. If it is under 25 MB and still fails, send support the id up-7f3a.

The second drops "could not" because the rule is the event, the value is the cause, and the rule is also the step. Form follows the three questions; the questions do not follow the form.

## The model as reader

A tool result returned to a model is an error message with a reader who has no other channel. It has no log, no support line, no patience to lose, and one turn to recover. The step must name what the model can change: the argument, the tool, or the fact that it must tell the user this cannot be done and why.

The official MCP server quickstart returns "Unable to fetch forecast data for this location" for a location outside the US, for a bad coordinate, and for a timeout. The model cannot choose a next call. Three messages fix it:

- No forecast for 51.5074, -0.1278: the NWS covers US locations only. Tell the user this tool cannot forecast London.
- Coordinates must be decimal degrees, latitude -90 to 90 and longitude -180 to 180. Got 144.9, -93.2.
- Forecast lookup timed out after 30 s. Call get_forecast again once; a second timeout means the service is down.
