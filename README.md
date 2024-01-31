# vct-match-data
Project to track match data from VCT LAN tournaments

This program is split into three main sections:
 * Add new data
 * View data
 * Update data

## Add new data
You can add match data to either a new tournament or an existing created tournament.
To create a new tournament you provide a list of maps that the tournament is played on, 
agents available in the tournament and teams that played.
You can also add a new Map, Agent or Team and how it's abbreviation to the referalls table.
Note: For Teams the abbreviation is entered in the name category and the full name is entered for
the abbreviation.

## View data
You can view a print out or plotted data from the database.
Data comes in 4 forms:
 * Maps
   * Pickrate
   * Sidedness
 * Comps
   * Pickrate
   * Winrate
   * Rating
 * Agents
   * Pickrate
   * Winrate
   * Rating
 * Teams
   * Matches
   * Wins
   * Pickrate (Print Only)
   * Winrate
   * Rating (Print Only)

## Update data
Deletes all data from maps, comps, agents and teams tables.
Reloads all data from the matches.