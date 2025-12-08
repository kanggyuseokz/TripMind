// components/ScheduleEditor.jsx
// 드래그 앤 드롭으로 일정을 편집할 수 있는 컴포넌트

import React, { useState, useRef } from 'react';

const ScheduleEditor = ({ schedule, pois = [], onScheduleChange }) => {
  const [editingSchedule, setEditingSchedule] = useState(
    JSON.parse(JSON.stringify(schedule))
  );
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showPoiSelector, setShowPoiSelector] = useState(false);
  const draggedEvent = useRef(null);

  // 시간대 옵션
  const timeSlots = [
    '오전', '점심', '오후', '저녁', '밤',
    '08:00', '09:00', '10:00', '11:00', 
    '12:00', '13:00', '14:00', '15:00',
    '16:00', '17:00', '18:00', '19:00', 
    '20:00', '21:00'
  ];

  // 아이콘 옵션
  const iconOptions = [
    { value: 'camera', label: '📸 관광', emoji: '📸' },
    { value: 'utensils', label: '🍽️ 식사', emoji: '🍽️' },
    { value: 'coffee', label: '☕ 카페', emoji: '☕' },
    { value: 'home', label: '🏠 숙소', emoji: '🏠' },
    { value: 'plane', label: '✈️ 공항', emoji: '✈️' },
    { value: 'car', label: '🚗 이동', emoji: '🚗' },
    { value: 'shopping-bag', label: '🛍️ 쇼핑', emoji: '🛍️' },
    { value: 'star', label: '⭐ 특별', emoji: '⭐' }
  ];

  // 드래그 시작
  const handleDragStart = (e, dayIndex, eventIndex) => {
    draggedEvent.current = { dayIndex, eventIndex };
    e.dataTransfer.effectAllowed = 'move';
    e.target.style.opacity = '0.5';
  };

  // 드래그 종료
  const handleDragEnd = (e) => {
    e.target.style.opacity = '1';
    draggedEvent.current = null;
  };

  // 드롭 허용
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  // 드롭 처리 (시간대 변경)
  const handleDrop = (e, targetDay, targetTime) => {
    e.preventDefault();
    
    if (!draggedEvent.current) return;

    const { dayIndex, eventIndex } = draggedEvent.current;
    const newSchedule = [...editingSchedule];
    
    // 원래 이벤트 제거
    const movedEvent = newSchedule[dayIndex].events.splice(eventIndex, 1)[0];
    
    // 새 시간대로 이벤트 이동
    movedEvent.time_slot = targetTime;
    
    // 타겟 날짜의 해당 시간대에 삽입
    const targetEvents = newSchedule[targetDay].events;
    const insertIndex = targetEvents.findIndex(e => e.time_slot === targetTime);
    
    if (insertIndex >= 0) {
      // 같은 시간대에 다른 이벤트가 있으면 그 앞에 삽입
      targetEvents.splice(insertIndex, 0, movedEvent);
    } else {
      // 해당 시간대가 없으면 적절한 위치에 삽입
      const timeOrder = timeSlots.indexOf(targetTime);
      let insertPos = 0;
      
      for (let i = 0; i < targetEvents.length; i++) {
        const eventTime = timeSlots.indexOf(targetEvents[i].time_slot);
        if (eventTime > timeOrder) break;
        insertPos = i + 1;
      }
      
      targetEvents.splice(insertPos, 0, movedEvent);
    }

    setEditingSchedule(newSchedule);
    onScheduleChange(newSchedule);
  };

  // 이벤트 수정
  const handleEventEdit = (dayIndex, eventIndex, field, value) => {
    const newSchedule = [...editingSchedule];
    newSchedule[dayIndex].events[eventIndex][field] = value;
    setEditingSchedule(newSchedule);
    onScheduleChange(newSchedule);
  };

  // 이벤트 삭제
  const handleEventDelete = (dayIndex, eventIndex) => {
    const newSchedule = [...editingSchedule];
    newSchedule[dayIndex].events.splice(eventIndex, 1);
    setEditingSchedule(newSchedule);
    onScheduleChange(newSchedule);
  };

  // 새 이벤트 추가
  const handleAddEvent = (dayIndex, timeSlot) => {
    const newEvent = {
      time_slot: timeSlot,
      place_name: '새 장소',
      description: '새 활동',
      icon: 'star',
      user_note: '',
      poi_rating: null  // ← 추가해서 0이 안 나오게 함
    };
    
    const newSchedule = [...editingSchedule];
    newSchedule[dayIndex].events.push(newEvent);
    setEditingSchedule(newSchedule);
    onScheduleChange(newSchedule);
  };

  // POI 선택하여 이벤트 수정
  const handlePoiSelect = (dayIndex, eventIndex, poi) => {
    const newSchedule = [...editingSchedule];
    const event = newSchedule[dayIndex].events[eventIndex];
    
    event.poi_name = poi.name; // ✅ 추가
    event.place_name = poi.name;
    event.description = poi.name; // ✅ 화면에 표시되는 텍스트
    event.latitude = poi.lat || poi.latitude;
    event.longitude = poi.lng || poi.longitude;
    event.poi_rating = poi.rating;
    
    setEditingSchedule(newSchedule);
    onScheduleChange(newSchedule);
    setShowPoiSelector(false);
  };

  return (
    <div className="schedule-editor">
      {/* 편집 툴바 */}
      <div className="mb-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-blue-800">
            ✏️ 편집 모드
          </span>
          <div className="text-xs text-blue-600">
            💡 드래그하여 시간 변경 | ✏️ 클릭하여 내용 수정 | ❌ X로 삭제
          </div>
        </div>
      </div>

      {/* 일정 표시 */}
      <div className="space-y-6">
        {editingSchedule.map((day, dayIndex) => (
          <div key={day.day} className="border border-gray-200 rounded-lg p-4">
            {/* 날짜 헤더 */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-gray-900">
                Day {day.day} - {day.date}
              </h3>
              
              {/* 시간대별 드롭존 */}
              <div className="flex gap-1">
                {timeSlots.slice(0, 5).map(timeSlot => (
                  <div
                    key={timeSlot}
                    className="px-2 py-1 bg-gray-100 rounded text-xs cursor-pointer hover:bg-blue-100"
                    onDragOver={handleDragOver}
                    onDrop={(e) => handleDrop(e, dayIndex, timeSlot)}
                    onClick={() => handleAddEvent(dayIndex, timeSlot)}
                    title={`${timeSlot}에 새 일정 추가`}
                  >
                    {timeSlot} +
                  </div>
                ))}
              </div>
            </div>

            {/* 이벤트 목록 */}
            <div className="space-y-2">
              {day.events.map((event, eventIndex) => (
                <div
                  key={`${dayIndex}-${eventIndex}`}
                  className="group flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:border-blue-300 cursor-move"
                  draggable
                  onDragStart={(e) => handleDragStart(e, dayIndex, eventIndex)}
                  onDragEnd={handleDragEnd}
                >
                  {/* 시간 */}
                  <select
                    className="w-20 text-sm border-0 bg-transparent font-medium text-blue-600"
                    value={event.time_slot}
                    onChange={(e) => handleEventEdit(dayIndex, eventIndex, 'time_slot', e.target.value)}
                  >
                    {timeSlots.map(slot => (
                      <option key={slot} value={slot}>{slot}</option>
                    ))}
                  </select>

                  {/* 아이콘 */}
                  <select
                    className="w-12 text-lg border-0 bg-transparent"
                    value={event.icon}
                    onChange={(e) => handleEventEdit(dayIndex, eventIndex, 'icon', e.target.value)}
                  >
                    {iconOptions.map(icon => (
                      <option key={icon.value} value={icon.value}>
                        {icon.emoji}
                      </option>
                    ))}
                  </select>

                  {/* 장소명 */}
                  <input
                    type="text"
                    className="flex-1 min-w-0 border-0 bg-transparent font-medium text-gray-900 focus:ring-2 focus:ring-blue-500 rounded px-2 py-1"
                    value={event.place_name || event.description}
                    onChange={(e) => handleEventEdit(dayIndex, eventIndex, 'place_name', e.target.value)}
                    placeholder="장소명"
                  />

                  {/* POI 선택 버튼 */}
                  {pois.length > 0 && (
                    <button
                      className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
                      onClick={() => {
                        setSelectedEvent({ dayIndex, eventIndex });
                        setShowPoiSelector(true);
                      }}
                    >
                      POI 선택
                    </button>
                  )}

                  {/* 메모 */}
                  <input
                    type="text"
                    className="w-32 text-xs border border-gray-200 rounded px-2 py-1 text-gray-600"
                    value={event.user_note || ''}
                    onChange={(e) => handleEventEdit(dayIndex, eventIndex, 'user_note', e.target.value)}
                    placeholder="개인 메모"
                  />

                  {/* 삭제 버튼 */}
                  <button
                    className="opacity-0 group-hover:opacity-100 w-6 h-6 text-red-500 hover:text-red-700"
                    onClick={() => handleEventDelete(dayIndex, eventIndex)}
                  >
                    ❌
                  </button>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* POI 선택 모달 */}
      {showPoiSelector && selectedEvent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full max-h-96 overflow-y-auto">
            <h3 className="text-lg font-bold mb-4">📍 장소 선택</h3>
            
            <div className="space-y-2">
              {pois.slice(0, 20).map((poi, index) => (
                <button
                  key={index}
                  className="w-full text-left p-3 border border-gray-200 rounded hover:border-blue-300 hover:bg-blue-50"
                  onClick={() => {
                    console.log("🔍 Selected POI:", poi); // ← 디버깅 추가
                    handlePoiSelect(selectedEvent.dayIndex, selectedEvent.eventIndex, poi);
                  }}
                >
                  <div className="font-medium">{poi.name}</div>
                  <div className="text-sm text-gray-600">
                    {poi.category} | ⭐ {poi.rating} | {poi.vicinity}
                  </div>
                </button>
              ))}
            </div>
            
            <button
              className="mt-4 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
              onClick={() => setShowPoiSelector(false)}
            >
              닫기
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ScheduleEditor;