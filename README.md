# Royalty App v.4

This is a flask app for calculating record label royalties. The app serves a REST API that needs to be consumed by a front end. The corresponding repo ["Royalty App Front End"](https://github.com/christopher-kirkley/frontend_royaltyapp) is a React front end built to work with the API. 

## Dependencies

- Flask
- SQLAlchemy
- Marshmallow
- Pandas
- Numpy
- Pytest (optional)

NOTE: Functional tests using Selenium require geckodriver, and needs to be included in PATH.

## RDBMS
It helps to know a bit about how the database is structured. At the core of the app is the idea of catalog items. Each catalog item represents a release, either tied to a single artist, or in the case of a compilation, assigned Various Artists. Each catalog item is represented in sales by a Version. These versions are identified by UPC (so a UPC, or a unique identifier must be provided for each Version. Tracks are tied to Catalog items, not Versions, so please note if track splits differ on versions, these should be assigned different Catalog items.

Artists are defined by Artist name, and some minimal info. Each artist is tied to Contact. These Contacts have access to many artists, and are used for managers or payout mediators, who collect and distribute royalties for many artist accounts.

## Endpoints

The API is based on REST principles,accessed via standard HTTPS requests in UTF-8 format to an API endpoint. API uses HTTP verbs for each action:  

GET	Retrieves resources  
POST	Creates resources  
PUT	Changes and/or replaces resources or collections  
DELETE	Deletes resources  

### Artists
`/artists`  
`/artists/{artistId}`  
`/artists/{artistId}/catalog`  
`/artists/{artistId}/track`  
`/contacts`  
`/contacts/{contactId}`  


### Catalog
`/catalog`     
`/catalog/{catalogId}`    
`/version`                 
`/version/{versionId}`     
`/track`                   
`/track/{trackId}`     
`/catalog/import-catalog`  
`/catalog/import-version`  
`/catalog/import-track` 

