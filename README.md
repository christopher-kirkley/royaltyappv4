# Royalty App v.4

This is a flask app for calculating record label royalties. The app serves a REST API that needs to be consumed by a front end. The corresponding repo "Royalty App Front End" is a React front end built to work with the API. 

## Dependencies

- Flask
- SQLAlchemy
- Marshmallow
- Pandas
- Numpy
- Pytest (optional)

NOTE: Functional tests using Selenium require geckodriver, and needs to be included in PATH.

## Endpoints

The API is based on REST principles,accessed via standard HTTPS requests in UTF-8 format to an API endpoint. API uses HTTP verbs for each action:

GET	Retrieves resources
POST	Creates resources
PUT	Changes and/or replaces resources or collections
DELETE	Deletes resources

### Catalog

/catalog                - All catalog items
/catalog/{catalogId}    - Catalog by record id
/version                - Version items (belonging to catalog)
/version/{versionId}    - Version by version id
/track                  - All tracks
/track/{trackId}        - Track by track id
/catalog/import-catalog - Import CSV in template of catalog items
/catalog/import-version - Import CSV in template of version items
/catalog/import-track   - Import CSV in template for track items

