# Beer Store Database Lookup
This project was primarily about using SQL along with trying out a new UI library for Python. The project uses SQLite and PyQT6. The rather simple UI resembles one an employee might use to help customers though many of the queries would better fit for the backend of a website, done automatically and sent to an email list. Since this is some dummy data I manually added the sensitive data was "encrypted" just to not be plain text. There is no way to alter data as most of the difficulty in adding or removing data would be the UI and encorpirating encryption which wasn't what I wanted to focus on here. Simply type what you seek into the texbox and click the desired button to do a search. The query directions are as follows:
*Display All Beers of a Style: type a beer style. The list includes Lager, Stout, Sour, Pale Ale, IPA, and Red Ale.
*All Customer Purchases: type customer ID. There are 10 customers, their IDs go from 1-10.
*Show purchase info: type purchase ID. There are 11 purchases, ID go from 1-11.
*Fetch Last X Purchases: type how many purchases you want to see.
*Customer's Preffered Types, Unpurchased: type customer ID. Meant to be a sort of recommendation for new beers in their preffered category.
*Customer's Preffered Types, Local Unpurchased: type customer ID. Also meant to act as a recommendation, though also trying to select only beer made in the customer's state.
*Customer's Local Beer: type state abbreviation or country name.
*Search by Beer Name: type name of beer or a keyword. Acts as a basic search bar.