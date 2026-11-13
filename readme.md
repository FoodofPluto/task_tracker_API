Path	Method	Purpose	Visibility	Success	Errors (400/401/403/404)
/auth/register	POST		public	201 Created	400
/auth/login	POST		public	200 OK	400, 401
/profile	GET		logged-in only	200 OK	401, 403, 404
/profile	PUT		logged-in only	200 OK	400, 401, 403
/commissions	POST		logged-in only	201 Created	400, 401, 403
/profile/commissions	GET		logged-in only	200 OK	401, 403
/commissions/int:id	GET		logged-in only	200 OK	401, 403, 404
/commissions/int:id	PATCH		logged-in only	200 OK	400, 401, 403, 404
/commissions/int:id	DELETE		logged-in only	204 No Content	400, 401, 403, 404


Task Tracker API – backend project in progress (branching lesson)