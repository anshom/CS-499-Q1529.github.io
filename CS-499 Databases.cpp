
----Database Management Report----

---Modified Date: 09/28/2020----

---Modified By: Aurthur Nshom---

#insert a single record into person Table

INSERT INTO person(person_id, first_name, last_name)
VALUES (7,'Aurthur', 'Nshom');


#Alter the person table to add a new column called email_address
#with datatype of varchar(50) not null

ALTER TABLE person
ADD COLUMN email_address varchar(50) NOT NULL;


#Update the person table with email addresses for each individual person making sure that there are no duplicates
UPDATE person 
SET email_address =(CASE WHEN person_id =1 THEN 'michaelphelps@gmail.com'
                         WHEN person_id =2 THEN 'katieledecky@gmail.com'
                         WHEN person_id =3 THEN 'usainbolt@yahoo.com'
                         WHEN person_id =4 THEN 'allysonfelix@gmail.net'
                         WHEN person_id =5 THEN 'michaeljordan@yahoo.com'
                         WHEN person_id =6 THEN 'dianataurasi@snhu.com'
                         WHEN person_id =7 THEN 'smonhan2019@gmail.com'
                       END)
WHERE person_id IN (1,2,3,4,5,6,7);


#Delete a record from the person table with specific first and last_name

DELETE FROM person
WHERE first_name ="Diana"
AND last_name ="Taurasi";


#Alter the contact-list table and add a new column Favorite

ALTER TABLE contact_list 
ADD COLUMN favorite varchar(10);


#Update the contact_list table and set favorite column with a value 'y' where contact_id is equal to 1

UPDATE contact_list
SET favorite = 'y'
WHERE contact_id = 1; 

#Update the contact_list table and set favorite with a value 'n' where contact_id is greater than 1

UPDATE contact_list 
SET favorite = 'n' 
WHERE contact_id <> 1;

#Insert new values into contact_list table as defined below

INSERT INTO contact_list(connection_id,person_id,contact_id,favorite) 
VALUES (DEFAULT, 7, 1, 'y'),
       (DEFAULT, 3, 2, 'n'),
       (DEFAULT, 4, 1, 'y');
       
#The below script create a new table called Image with defined columns with an auto increment on the primary key

CREATE TABLE image(
    image_id int(8) NOT NULL AUTO_INCREMENT,
    image_name varchar(50) NOT NULL,
    image_location varchar(250) NOT NULL,
    PRIMARY KEY(image_id)
    )AUTO_INCREMENT = 1;
    
#Create a new table called message_image as defined below

CREATE TABLE message_image(
    message_id int(8) NOT NULL,
    image_id int(8) NOT NULL,
    PRIMARY KEY (message_id, image_id)
    );

#Insert new records into image table with new images and location

INSERT INTO image(image_id, image_name,image_location)
VALUES (DEFAULT, 'image1', 'location1'),
       (DEFAULT, 'image2', 'location2'),
       (DEFAULT, 'image3', 'location3'),
       (DEFAULT, 'image4', 'location4'),
       (DEFAULT, 'image5', 'location5');

INSERT INTO message_image(message_id, image_id) 
VALUES (1, 1),
       (2, 2),
       (3, 3),
       (4, 4),
       (5, 5);


SELECT  s.first_name AS "First Name", 
        s.last_name AS "Last Name", 
        r.first_name AS "First Name", 
        r.last_name AS "Last Name", 
        m.message_id AS "MessageID", 
        m.message AS "Message", 
        m.send_datetime AS "Timestamp"
FROM 
     person s, 
     person r,
     message m
WHERE 
    s.first_name = "Michael"
    AND s.last_name ="Phelps"
    AND m.sender_id = s.person_id
    AND m.receiver_id = r.person_id;
    
SELECT COUNT(m.message_id) AS "Count of Messages",
    p.person_id AS "Person ID", 
    p.first_name AS "First Name", 
    p.last_name AS "Last Name"
    
FROM 
     person p,
    message m 
   
WHERE 
     p.person_id = m.sender_id 
GROUP BY p.person_id, 
         p.first_name, 
         p.last_name;

         
SELECT mi.message_id AS "Message ID", 
    MIN(m.message) AS "Message", 
    MIN(m.send_datetime) AS "Timestamp", 
    MIN(i.image_name) AS "First image name", 
    MIN(i.image_location) AS "First image location" 
    
FROM message m 
    INNER JOIN message_image mi  
    ON m.message_id = mi. message_id
    INNER JOIN image i
    ON i.image_id = mi.image_id
    GROUP BY mi.message_id;

  
  
        
