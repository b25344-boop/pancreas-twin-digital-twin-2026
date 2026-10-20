# Project Pancreas Twin: 20-Minute Video Walkthrough Script

**For:** Happiest Health Digital Twin Challenge 2026 (Unstop). The brief asks for a video of at least 20 minutes; the submission form describes a 15 to 20 minute demo video. This script is sized to land just over 20 minutes, which meets both.
**Deck:** `Project_Pancreas_Twin_Deck.pptx` (15 slides). **Demo:** `streamlit run app.py`.
**Pace:** the timecodes below assume 140 words per minute (`video/build_video.py --timecodes` recomputes them). The rendered narration runs slower, about 130 words per minute plus pauses, so the video is about 20.5 minutes.
**Format:** each `## ` section is one segment of the video. Lines starting with `>` are stage directions and are not spoken. Everything else is narration.
**Numbers:** every number below matches `README.md`, `fresh/results.json`, `fresh/personalize_results.json`, `baseline_results.json` and `fusion_ablation_results.json`.

---

## Slide 1: Project Pancreas Twin [00:00 - 01:09]

> Title slide on screen. Speak slowly, this sets the tone.

Hello, and thank you for watching. My name is Akhilesh K S, and I lead team PancreasTwin from XLRI, Xavier School of Management, Delhi NCR campus. This is our submission to the Happiest Health Digital Twin Challenge twenty twenty six.

Project Pancreas Twin is a digital twin of a person's glucose. It watches their continuous glucose monitor, their meals, their activity and a few facts from their health record, and it predicts where their blood sugar is heading over the next one to two hours. Over the next twenty minutes I will cover the problem, the data, the model, how well it works when tested honestly, and the dashboard running live. One thing up front: during the project we rebuilt our whole evaluation from scratch, and in one place the rebuild told us an earlier claim of ours was too strong. I will show you exactly where, because we think honesty is part of what makes a digital twin trustworthy.

## Slide 2: The Clinical Burden [01:09 - 02:09]

> Point to the three cards from left to right.

Why does this matter? The ICMR INDIAB national survey, published in 2023, estimates about one hundred and one million Indian adults with diabetes and another one hundred and thirty six million with prediabetes. Control is usually tracked with HbA1c, a three month average. That average hides the daily story: sharp spikes after meals, and dangerous lows at night. Repeated spikes damage small blood vessels over time, and a glucose level below seventy milligrams per decilitre can cause confusion, falls and emergency visits.

Continuous glucose monitors show glucose every few minutes, but they are mostly reactive. They alarm when glucose has already crossed a threshold such as one hundred and eighty. By then the meal is absorbed and the patient can only watch. Our question was simple. What if the warning came an hour earlier, while there was still time to act?

## Slide 3: Why the 60-Minute Horizon [02:09 - 03:02]

> Walk across the three timing cards.

How far ahead should a forecast look? Fifteen to thirty minutes is too short. Digestion is already under way, and there is no room for a lifestyle response.

Sixty minutes is the actionable window. An hour is enough for a short brisk walk after a meal. Working muscles pull glucose out of the blood through a pathway that does not need insulin, called GLUT4 translocation. An hour is also enough to take fifteen grams of fast carbohydrate if the forecast points to a low.

Two hours is useful for planning, but behaviour becomes less predictable, so we expect it to be less precise. That is why every result is reported at both sixty and one hundred and twenty minutes, always against a simple baseline.

## Slide 4: Data Ingestion and Harmonization [03:02 - 04:16]

> Left card first, then the right card.

A twin is only as good as its data. We surveyed and downloaded seventeen open clinical datasets, about eleven point six gigabytes and more than two hundred and forty seven million records. Each one, with its licence, is listed in our repository.

Four cohorts carry the right mix of signals, and we model on them: PhysioNet CGMacros with forty five people, BIG IDEAs with sixteen people with prediabetes, HUPA UCM with people with type one diabetes, and the Shanghai dataset of patients with type two diabetes and measured lab values.

When we rebuilt our evaluation from scratch, we found and fixed four problems in our first pipeline: only twenty of the one hundred and nine Shanghai files had loaded, two patients sat in both training and testing, many points were interpolated rather than real readings, and one patient dominated the rows. The rebuild uses four hundred and forty two thousand real readings from one hundred and eighty four patients, weights every patient equally, and covers type one, type two, prediabetes and healthy adults.

## Slide 5: Multi-Modal Architecture [04:16 - 05:15]

> Left tower, middle tower, then the fusion card on the right.

The twin has two towers, because a person has two kinds of information. The first tower holds what does not change during the day: age, body mass index, baseline HbA1c and medication. The second tower reads the last four hours, minute by minute: glucose and its rate of change, heart rate, activity, carbohydrates and the time of day, through a two layer recurrent network.

The two are joined to produce a sixty minute forecast with a ninety percent confidence cone, a two hour forecast and a spike warning. Training penalises underestimating a low two and a half times more, because missing a dangerous low is worse than a false alarm.

Alongside this network we train gradient boosted trees with LightGBM. LightGBM turned out to be our strongest and most reliable forecaster, and it drives the headline numbers.

## Slide 6: Headline Result [05:15 - 06:57]

> This is the most important slide. Point at the 60-minute panel, then the 120-minute panel, then the cards.

Any glucose forecaster must first beat persistence, which says glucose in an hour will equal glucose now. It sounds naive, but glucose changes smoothly, so it is a tough baseline.

Our headline test is patient disjoint five fold cross validation on all one hundred and eighty four patients. We split patients into five groups, train on four and test on the fifth, five times. Every patient is tested exactly once, always by a model that has never seen them.

At sixty minutes, persistence has an error of thirty one point one four milligrams per decilitre. Our best model, LightGBM with glucose history, meal logs and the health record, gets twenty five point eight five, plus or minus one point zero three across folds. That is seventeen percent lower error. At two hours, persistence is forty four point three three and our model is thirty five point six five, twenty percent lower. The gap grows with the horizon, as it should.

The ladder of models tells the same story: ridge regression beats persistence, LightGBM on glucose alone does better, and meal logs help further. The small plus or minus after each number is the spread across the five folds, so the result is stable, not a lucky split. By cohort, the sixty minute error ranges from about eighteen and a half for the prediabetes group to about twenty nine for type one diabetes, which is the hardest group to predict.

## Slide 7: Secondary Evidence [06:57 - 07:54]

> Point at the chart, then at the right card.

Our original evaluation used one held out set of seventeen patients, which we now treat as secondary. There, persistence is thirty two point six six at sixty minutes, and LightGBM is twenty seven point nine three. At two hours, forty eight point zero seven against thirty nine point five four.

Seventeen people is a small sample, so we checked it directly. The rebuilt pipeline, scored on the same seventeen people, gets twenty six point three three and thirty six point zero five, and the two pipelines agree on persistence within about one milligram per decilitre. Both measure the same thing, and both say the twin clearly beats the baseline at one hour and at two hours. The original numbers were real; the rebuild simply tests them on ten times more people.

## Slide 8: Multi-Modal Fusion [07:54 - 09:14]

> This is the honest correction slide. Point at the L4 bar on the chart, then at the right card.

Now the slide where we correct ourselves. Which signals actually earn their place? We kept the model fixed and added one group of signals at a time.

On the seventeen patient split, the static health record looked like the star. It cut the error by zero point seven four at sixty minutes and one point three three at two hours, and that was significant. But in the five fold rebuild, across one hundred and fifty three patients with measured values, the gain shrank to zero point one five at sixty minutes, only borderline, and to nothing at two hours. It was real for those seventeen people, but it does not generalise, and our deck and README now say so.

Heart rate and activity, in the form these datasets provide them, added almost nothing. What does generalise is meal logging: zero point four two better at sixty minutes and zero point five six at two hours, across all patients. The product lesson is clear. The twin improves when patients log meals, so the app should make meal logging effortless, for example with a photo or a single tap.

## Slide 9: Closing the Loop [09:14 - 11:29]

> Point to the two bar charts, then the three cards.

Is this really a digital twin, or just a forecast? The National Academies define a digital twin as a virtual model updated with data from its own physical counterpart, and a 2025 review found only about twelve percent of published healthcare twins meet that bar. So we tested whether our twin learns from the one patient it is watching.

As each reading arrives, the twin checks the forecasts it made earlier against what actually happened. If it has been running too high or too low for this patient over the last twenty four hours, it corrects its next forecast by that amount, shrunk toward zero when it has seen little data. For example, if over the past day the twin's one hour forecasts for a patient have run about eight points too high, the next forecast is lowered by close to eight points. It only uses outcomes that are already known, so nothing leaks from the future, and it needs no retraining and no cloud.

The settings were fixed before testing. On the same five fold test, the sixty minute error falls from twenty five point eight five to twenty five point four seven, and the two hour error from thirty five point six two to thirty four point five four. That is eighteen and twenty two percent better than persistence. About seventy percent of patients improve, every cohort improves, and clinical safety improves at both horizons. And the longer the twin knows a patient, the more it helps: a seventy two hour memory does better than twenty four hours, and a six hour memory barely helps at all. The gain per forecast is small, but it is very consistent, and the paired test across patients gives a p value below one in a trillion. This is the simplest form of personal learning. Learning each patient's own response to meals and exercise is the next step.

## Slide 10: Clinical Safety [11:29 - 12:59]

> Point to the zones on the Clarke grid as you name them.

Average accuracy is not enough in medicine. We also need to know whether errors are dangerous. The Clarke error grid answers that. Zone A means within twenty percent of the truth. Zone B means off, but not harmful. Zone E, the worst, means a forecast that would lead to the opposite treatment.

In the five fold test, the best sixty minute model puts ninety seven point two percent of forecasts in zones A and B, and about one in ten thousand in zone E. One honest note: persistence also scores high on this grid, because a lagged forecast usually lands in zone B. So error in milligrams per decilitre is our main metric, and the grid is the safety check.

The ninety percent confidence cone covered ninety one point eight percent of outcomes, so it is well calibrated. Alerts arrive a median of forty to fifty minutes before glucose crosses one hundred and eighty. Raw alerts fired too often, so we added a thirty minute quiet window after each alert, which cut false alarms by about eighty one percent, from one hundred and seventy seven to thirty four per hundred patient hours. Thirty four is still too many for daily use, and bringing it down further is on our roadmap.

## Slide 11: Counterfactual Simulation [12:59 - 13:58]

> Point at the trajectory and the shaded cone.

A twin should also answer what if. On the left is a real forecast for one test patient, with its confidence cone widening when the model is less sure.

Suppose the twin predicts a spike to about two hundred and fifteen after lunch. The patient asks: what if I walk for fifteen minutes now? The twin redraws the forecast with the walk included, and the peak comes down by about thirty six milligrams per decilitre, which can keep the curve inside the safe range.

To be clear, in this prototype the walking effect is a simple rule sized to published post meal walking studies, not a learned model, and it never pushes a forecast into the low range. Learning it from data is on our roadmap. Even so, it turns a scary number into a concrete choice.

## Slide 12: Edge Deployment [13:58 - 14:36]

> Left to right across the three cards.

The twin runs on the device, not in the cloud. The network checkpoint is about two hundred kilobytes, and one forecast takes under a millisecond on a laptop processor, and about a fifth of a millisecond on its integrated graphics, small enough for a phone and in principle a watch. That means no per patient cloud cost, and continuous health data never has to leave the phone, which makes it far easier to design for India's data protection law. Formal compliance would still need a legal review before launch.

## Slide 13: The Clinical Decision Support App [14:36 - 14:51]

> Read the feature list briefly, then switch to the browser for the live demo.

The prototype is a Streamlit web app, app.py in our repository, with a patient switcher, a day scrubber, a forecast chart, a triage badge and a what if walk toggle. Let me show it live.

## Live Demo: Streamlit Dashboard [14:51 - 16:25]

> Switch to the browser running `streamlit run app.py`. Keep the demo to about two minutes.
> Sidebar: show the patient selector and the profile card.

On the left is the patient selector. I pick one of the held out test patients, and their profile card shows age, body mass index, HbA1c and medication.

> Move the day scrubber slider slowly.

The day scrubber moves us through the day. The chart shows four hours of real glucose, then the sixty minute and two hour forecasts with confidence cones, against the green target band of seventy to one hundred and eighty. The lower panel shows activity.

> Stop on a point where glucose is rising after a meal. Point at the triage badge.

Here glucose is climbing after a meal. The twin predicts it will cross one hundred and eighty within the hour, so the badge shows a red spike alert. A coming low would turn it amber.

> Tick the "Simulate Intervention: 15-min Post-Meal Walk" checkbox.

Now I tick the fifteen minute walk. The forecast is redrawn and the projected peak comes down. That is the moment we want the patient to have: an early warning and a concrete action with a visible effect.

> Scroll down to the scorecard.

At the bottom, the scorecard shows the same numbers you saw in the deck. On the left, the headline five fold result on one hundred and eighty four patients, with the seventeen patient split below it. On the right, fusion, safety and alerting, including the honest finding that meal logging matters more than the static health record. Nothing on this screen is hand typed: it is read from the results files the code produces.

> Switch back to the slides.

## Slide 14: Regulatory Strategy and Ethics [16:25 - 17:20]

> Left to right across the three cards. The middle card is the key message.

We position Pancreas Twin as clinical decision support, which would be treated as software as a medical device. The most important line in our design is in the middle: the twin never doses insulin. It does not control a pump, calculate a bolus or change a prescription. It warns early and suggests lifestyle actions, with a clear disclaimer on every screen.

It is also auditable. The headline model is gradient boosted trees with inspectable features, there is no generative model writing free text advice, and if a sensor stream drops out, the system can fall back to simpler models such as ridge regression. Everything shown here is reproducible from our repository, with a verification script that checks the patient splits, the units, and that every model beats persistence.

## Slide 15: Commercialization and Roadmap [17:20 - 18:49]

> Left card, then right card, then close looking at the camera.

How does this reach people? Mainly business to business to consumer: diabetes clinics and hospital networks offer it to patients, insurers and wellness programmes use it to reduce emergency visits, and the HL7 FHIR standard lets it plug into health records. A patient subscription can unlock extras such as meal what if simulations.

Phase one is what you saw today. Phase two, in early twenty twenty seven, is a prospective study with about fifty patients, where we will also test the walking effect properly. Then a CDSCO pre submission in India, and pilots with diabetes clinic chains, with native integration into Apple Health and Google Health Connect so the twin can read the sensors people already wear.

Three things to remember. First, the twin forecasts an hour ahead, early enough to act, and beats persistence by seventeen percent at one hour and twenty percent at two hours on one hundred and eighty four unseen patients, rising to eighteen and twenty two percent when it learns from each patient. Second, we tested ourselves hard, and when the evidence said a claim was too strong, we changed it. Third, it runs privately on the device and never doses insulin.

Everything is in our GitHub repository. Thank you for your time.
