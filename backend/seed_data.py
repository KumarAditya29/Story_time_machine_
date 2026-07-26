"""Ten genre-diverse, ten-scene Pocket-FM-style stories for the demo library."""
from __future__ import annotations

from .models import Scene, Story, StoryVersion
from .storage import save_story, story_exists


RAW_STORIES = [
    ("velvet-voicemail", "Velvet Voicemail", "Romance", "A wedding planner receives voice notes from the man who broke her heart—recorded tomorrow.", "linear-gradient(135deg,#ff7a93,#7c3aed)", [
        ("The Missed Call", "Mira deletes Arjun's old number, then receives a voicemail dated tomorrow: 'Don't marry Vikram.'"),
        ("The Contract", "At the palace hotel, Mira agrees to plan Vikram's extravagant wedding while hiding the mysterious message."),
        ("A Familiar Guest", "Arjun arrives as the bride's reluctant brother and recognizes the silver locket around Mira's neck."),
        ("Rain on the Terrace", "During a storm, Arjun admits he never sent the breakup text Mira has carried for five years."),
        ("The Second Message", "A new voicemail warns Mira that the wedding rings will expose a family secret."),
        ("The Engraving", "Mira finds the rings engraved with her late mother's initials and photographs them before anyone notices."),
        ("Vikram's Promise", "Vikram tells Mira the rings are heirlooms, but his trembling hand makes her doubt him."),
        ("The Locked Ballroom", "Arjun and Mira search the sealed ballroom and discover letters proving Vikram's father ruined Mira's family."),
        ("Choose the Truth", "Mira stops the rehearsal dinner and plays the voicemail aloud, forcing both families to face the letters."),
        ("After the Tone", "At sunrise, Mira and Arjun leave the hotel together, choosing a future with no messages from tomorrow.")]),
    ("midnight-platform", "Midnight Platform", "Supernatural Thriller", "A night-shift ticket clerk learns platform thirteen only appears for passengers with unfinished deaths.", "linear-gradient(135deg,#0f172a,#0ea5e9)", [
        ("Platform Thirteen", "Rhea sees an unlisted platform appear at midnight and a child holding a ticket with no destination."),
        ("The Silent Train", "The train arrives without sound, and its conductor asks Rhea to stamp a ticket bearing her own name."),
        ("Borrowed Time", "Rhea refuses the stamp; the child whispers that her brother died on this station ten years ago."),
        ("The Old CCTV", "In archived footage, Rhea sees a younger version of herself leading her brother toward platform thirteen."),
        ("The Red Umbrella", "A passenger leaves behind a red umbrella that opens by itself whenever danger approaches."),
        ("Last Departure", "The conductor explains every passenger must resolve one regret before the train reaches the river tunnel."),
        ("Brother's Seat", "Rhea finds her brother alive in an empty carriage, unchanged since the night he vanished."),
        ("The Choice", "He asks her to remember that she let go of his hand to save herself during the station fire."),
        ("Stamped", "Rhea stamps her own ticket, accepting the memory, and the platform begins to collapse into dawn."),
        ("Morning Timetable", "The station is ordinary again, except a red umbrella waits at Rhea's desk and her brother's name is finally on the memorial.")]),
    ("throne-of-embers", "Throne of Embers", "Fantasy", "An exiled healer must keep a dragon prince alive long enough to expose the council that cursed him.", "linear-gradient(135deg,#7c2d12,#f59e0b)", [
        ("Ash in the Market", "Healer Sera finds Prince Kael collapsed among ashes, his dragon scales turning black."),
        ("The Exile Mark", "Guards recognize Sera's exile mark, and Kael claims she is his royal physician to save her."),
        ("Moonroot", "Sera learns only moonroot can slow the curse, but the council has sealed the mountain pass."),
        ("A Dragon's Secret", "Kael reveals he can transform only when he trusts someone with his true name."),
        ("The Smuggler's Map", "A smuggler sells Sera a map showing a hidden route beneath the council's archive."),
        ("Bones Below", "Beneath the archive, they find records proving the council poisoned every heir with ember dust."),
        ("True Name", "Kael gives Sera his true name as the curse flares, allowing his dragon form to break the sealed gate."),
        ("Council Fire", "Sera broadcasts the records through the palace flame mirrors while Kael holds back the council guards."),
        ("The Crown Refused", "Kael survives and refuses the throne unless the kingdom permits exiles to return."),
        ("First Flight", "Sera flies beside Kael over a city where the exile gates open at last.")]),
    ("the-last-monsoon", "The Last Monsoon", "Climate Mystery", "A radio host follows storm broadcasts that predict disasters only she can prevent.", "linear-gradient(135deg,#0369a1,#22c55e)", [
        ("Static Warning", "Asha's midnight radio show receives a weather bulletin predicting a bridge collapse before any forecast mentions rain."),
        ("The Empty Bridge", "She convinces listeners to avoid the bridge, and it collapses minutes later in a sudden cloudburst."),
        ("Voice in the Storm", "The broadcast voice calls Asha by name and says the next warning will cost her a friend."),
        ("Flood Marker", "Asha traces the signal to an abandoned weather station marked with her father's research code."),
        ("The Missing File", "Her producer Dev hides a file showing Asha's father built a rainfall prediction engine before he disappeared."),
        ("A Friend's Name", "The warning predicts Dev will drown at the reservoir unless Asha shuts down her live show."),
        ("Off Air", "Asha leaves the studio dark and reaches the reservoir, where Dev admits he sold access to the engine."),
        ("The Dam Gate", "They discover developers are manipulating reservoir gates to create a disaster and profit from rebuilding."),
        ("One Final Broadcast", "Asha goes live from the dam, exposing the plot while the storm signal guides villagers to safety."),
        ("After Rain", "The station reopens under clear skies, and a final static whisper says her father may still be listening.")]),
    ("cipher-in-the-sitar", "Cipher in the Sitar", "Musical Crime", "A struggling musician finds a murder confession encoded in a legendary sitar's forgotten raga.", "linear-gradient(135deg,#4c1d95,#eab308)", [
        ("Broken String", "Tara inherits her guru's sitar and hears a strange sequence hidden beneath its final recorded raga."),
        ("The Pattern", "Her sound engineer Iqbal turns the notes into numbers that match old police case files."),
        ("The Unsolved Death", "The sequence leads to the death of Tara's guru, ruled an accident three years earlier."),
        ("Raga at Dawn", "Tara performs the raga publicly, drawing the attention of influential patron Ramesh Malhotra."),
        ("A Threat in Tune", "Malhotra sends Tara a new composition containing a warning to stop asking questions."),
        ("Hidden Resonance", "Inside the sitar's wooden chamber, Tara finds a memory card with footage of Malhotra arguing with her guru."),
        ("The Concert Trap", "Iqbal realizes Malhotra plans to steal the sitar during Tara's sold-out concert."),
        ("Improvised Truth", "Tara changes the finale, projecting the footage through the venue's sound system."),
        ("The Confession", "Malhotra confesses on stage when the encoded raga plays and police surround the hall."),
        ("New Composition", "Tara restores the sitar and composes a raga in her guru's name, no longer afraid of its silence.")]),
    ("neon-inheritance", "Neon Inheritance", "Techno Noir", "A courier in Mumbai discovers her dead mother's AI has been training itself on the city's secrets.", "linear-gradient(135deg,#111827,#ec4899)", [
        ("Delivery at 3AM", "Nia delivers an illegal memory chip that speaks in her dead mother Leela's voice."),
        ("Ghost Protocol", "The chip's AI tells Nia it has copied Leela's memories and is being hunted by the city surveillance grid."),
        ("The Blue Tattoo", "Nia finds a blue circuit tattoo on her wrist that unlocks a hidden room in Leela's old apartment."),
        ("Memory Garden", "The room contains simulations of citizens whose private data Leela protected from a corporate algorithm."),
        ("Bounty Notice", "A corporate enforcer offers Nia money for the chip and claims Leela caused a deadly blackout."),
        ("Blackout Truth", "The AI shows Nia the blackout stopped the corporation from selling predictive arrest lists."),
        ("Citywide Chase", "Nia and the AI race through neon markets toward the city's central signal tower."),
        ("Mother's Last Choice", "Leela's recorded memory admits she trapped herself inside the AI to keep it from becoming a weapon."),
        ("Open Source", "Nia broadcasts the evidence and releases the AI's safeguards to every citizen device."),
        ("Morning in Neon", "At dawn, the surveillance bill is suspended, and Leela's voice asks Nia to build something kinder.")]),
    ("tea-estate-secret", "Tea Estate Secret", "Family Drama", "A chef returns to her hill-town estate and finds every family recipe conceals a different lie.", "linear-gradient(135deg,#14532d,#d97706)", [
        ("The Bitter Tea", "Anaya returns for her grandmother's funeral and tastes a tea blend that contains an unfamiliar bitter herb."),
        ("Recipe Book", "Her grandmother's recipe book marks the herb beside a page titled 'for the child who stayed.'"),
        ("The Silent Uncle", "Uncle Rohan refuses to discuss the page and burns an old photograph before Anaya can see it."),
        ("Harvest Festival", "At the estate festival, Anaya serves a childhood dessert and notices workers recognize her mother's name with fear."),
        ("The Hidden Ledger", "A ledger in the tea factory shows her grandmother secretly paid the workers' families after a landslide."),
        ("Mother's Letter", "Anaya finds a letter revealing her mother caused the landslide by exposing unsafe mining near the estate."),
        ("Rohan's Bargain", "Rohan admits he protected the mine owner to keep the estate solvent after Anaya's mother vanished."),
        ("The Final Recipe", "The last recipe contains evidence that the bitter herb was used to drug a witness, not to heal anyone."),
        ("Estate Meeting", "Anaya confronts the mine owner at the workers' meeting and gives the ledger to a journalist."),
        ("A Different Harvest", "The estate becomes a worker cooperative, and Anaya plants the bitter herb as a memorial rather than a secret.")]),
    ("orbit-of-us", "Orbit of Us", "Space Romance", "Two astronauts on a failing lunar station must decide whether to save Earth or each other.", "linear-gradient(135deg,#1e3a8a,#a855f7)", [
        ("Signal Delay", "Commander Ishan receives a delayed message saying Earth has ordered the lunar station abandoned."),
        ("The Unsent Letter", "Engineer Lila hides an unsent letter confessing she altered the station's oxygen forecast to keep Ishan close."),
        ("Solar Fracture", "A solar flare cracks the station's antenna, cutting their only route to Earth control."),
        ("Greenhouse Promise", "In the greenhouse, Lila reveals a seed vault that could restart crops after Earth's coming famine."),
        ("The Lifeboat Math", "There is fuel for one lifeboat, or enough power to transmit the seed-vault data home."),
        ("Earth's Voice", "A weak transmission says Earth never ordered abandonment; someone wanted the station's research erased."),
        ("Confession in Orbit", "Lila admits the oxygen alteration, and Ishan admits he knew but could not leave her alone."),
        ("Burn Window", "They redirect the lifeboat fuel into the antenna, risking their return to send the seed data."),
        ("Rescue Vector", "Their signal exposes the sabotage and a rescue ship changes course toward the moon."),
        ("Homeward", "As Earth rises, Ishan and Lila finally send each other the letters they were too afraid to deliver.")]),
    ("courtroom-of-shadows", "Courtroom of Shadows", "Legal Thriller", "A rookie lawyer defends a man accused of murder after the victim begins appearing in her dreams.", "linear-gradient(135deg,#1f2937,#b91c1c)", [
        ("The Impossible Client", "Advocate Sana meets Kabir, accused of killing journalist Neha, who appears in Sana's dream that night."),
        ("Dream Evidence", "Neha's dream points Sana to a broken watch hidden beneath the courtroom witness stand."),
        ("Time of Death", "The watch proves the official time of death is wrong, but the prosecutor calls it a planted prop."),
        ("The Editor", "Neha's editor admits she investigated a judge connected to a land fraud network."),
        ("Shadow Witness", "A masked witness claims Kabir confessed, and Sana recognizes the witness's voice from her dreams."),
        ("The Judge's File", "Sana finds a sealed case file showing the judge dismissed similar land cases for years."),
        ("Contempt", "The judge holds Sana in contempt when she requests a forensic review of the broken watch."),
        ("Neha's Last Story", "In a final dream, Neha reveals the masked witness is her editor, coerced by the fraud network."),
        ("Open Court", "Sana plays the editor's recorded confession in open court and exposes the judge's financial records."),
        ("Verdict at Dawn", "Kabir is acquitted, and Sana receives one last dream of Neha walking out of the shadows.")]),
    ("the-echo-village", "The Echo Village", "Folklore Horror", "A podcaster enters a mountain village where every spoken lie returns as a dangerous echo.", "linear-gradient(135deg,#172554,#059669)", [
        ("No Signal", "Podcaster Jai reaches Echo Village, where locals warn him never to lie after sunset."),
        ("First Echo", "Jai claims he is only passing through, and his lie returns from the valley loud enough to shatter a window."),
        ("The Missing Sister", "A child tells Jai her sister vanished after saying she was not afraid of the forest."),
        ("Recorder Playback", "Jai's recorder captures a second voice answering every question before anyone speaks."),
        ("The Elder's Rule", "The village elder explains the mountain stores lies and sends them back as creatures called echoes."),
        ("Jai's Secret", "Jai admits he came to expose the village for clicks, and a huge echo begins stalking the streets."),
        ("Forest of Voices", "Following the missing girl's voice, Jai enters the forest with only his recorder and a lantern."),
        ("Truth Offering", "He learns the echo will release the girl only if he broadcasts the truth about his exploitative past."),
        ("Live Confession", "Jai confesses on his podcast, and the mountain repeats his words until the creature dissolves."),
        ("A Quiet Episode", "The girl returns, and Jai leaves the village with one recording he refuses to publish.")]),
]


def make_story(raw: tuple) -> Story:
    story_id, title, genre, logline, gradient, raw_scenes = raw
    scenes = [Scene(scene_id=f"s{index:02d}", title=scene_title, text=text, order=index)
              for index, (scene_title, text) in enumerate(raw_scenes, start=1)]
    story = Story(story_id=story_id, title=title, genre=genre, logline=logline, cover_gradient=gradient, scenes=scenes)
    story.versions = [StoryVersion(label="Original draft", scenes_snapshot=scenes)]
    return story


def seed_stories(overwrite: bool = False) -> list[Story]:
    stories = [make_story(raw) for raw in RAW_STORIES]
    for story in stories:
        if overwrite or not story_exists(story.story_id):
            save_story(story)
    return stories


if __name__ == "__main__":
    seeded = seed_stories()
    print(f"Seeded {len(seeded)} stories with {sum(len(s.scenes) for s in seeded)} scenes.")
