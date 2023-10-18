# User Roles Documentation

## Description

User roles are type of users in SAWPS affecting what they can do in the system. 
There are currently 10 roles:

| Role                          | Description                                                                                                                                      |
|-------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| **Unnamed user**              | A user on the internet who is not registered with the site.                                                                                      |
| **Floating user**             | A registered user who does not have an organisation and needs to request addition to/of organisation.                                            |
| **Organisation member**       | A user who is registered on the site and part of an organisation.                                                                                |
| **Organisation manager**      | A user who is registered on the site and part of an organisation that can add other members to the site.                                         |
| **Provincial data consumer**  | A decision-maker type user who has access to the site to consume aggregate data about the region but not property specific information.          |
| **National data consumer**    | A national decision-maker type user who has access to the site to consume aggregate data about the region but not property specific information. |
| **Provincial data scientist** | A provincial data reviewer that can view data down to property lever and use the data to e.g. planning and permitting.                           |
| **National data scientist**   | A national data reviewer that can view data down to property lever and use the data for e.g. planning and permitting.                            |
| **Site administrator**        | A SANBI staff member with superuser access to all functionality on the site and the Django admin page.                                           |
| **Statistician**              | A user who has access to the statistics portal and R code uploader.                                                                              |

## Assigning Roles

This section shows few method on how a user can obtain a role.


| Role                          | Assignment Method                                                                                                                                 |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **Organisation member**       | User makes [organisation request](./user-profile/request-organisation.md), or<br/>Site administrator invites a user to an organisation as member. |
| **Organisation manager**      | Site administrator invites a user to an organisation as manager.                                                                                  |
| **Provincial data consumer**  | Add `Provincial data consumer` to user group from User Table in [Django Admin page](../../administrator/manual/django-admin.md).                  |
| **National data consumer**    | Add `National data consumer` to user group from User Table in [Django Admin page](../../administrator/manual/django-admin.md).                    |
| **Provincial data scientist** | Add `Provincial data scientist` to user group from User Table in [Django Admin page](../../administrator/manual/django-admin.md).                 |
| **National data scientist**   | Add `National data scientist` to user group from User Table in [Django Admin page](../../administrator/manual/django-admin.md).                   |
| **Site administrator**        | Set user as staff and superuser from User Table in [Django Admin page](../../administrator/manual/django-admin.md)  .                             |