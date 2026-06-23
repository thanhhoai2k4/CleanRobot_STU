std_msgs/Header header
string id # identify vd: rac_01, rac_02
string class_name # trai_nhua, tui_ni_long,...
float32 confidence # điểm tin cậy

geometry_msgs/PoseStamped pose #Định vị trong bản đồ của robot.
bool reachable # có thể  đến rác không: vd: nếu nhìn thấy rác nhưng vì bản thân robot quá to ko thể nhặc nên bỏ qua luôn.
string status # trạng thái công việc.