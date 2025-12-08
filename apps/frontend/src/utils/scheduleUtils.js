// utils/scheduleUtils.js
// 항공편 시간에 맞춰 여행 스케줄을 조정하는 유틸리티 함수

/**
 * 시간 포맷팅 함수
 */
const formatTime = (isoString) => {
  if (!isoString) return '-';
  try {
    const date = new Date(isoString);
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit', hour12: false });
  } catch {
    return '-';
  }
};

/**
 * 항공편 시간에 맞춰 스케줄을 조정하는 메인 함수
 */
export const adjustScheduleWithFlightTimes = (schedule, selectedFlight) => {
  if (!selectedFlight || !schedule || schedule.length === 0) {
    return schedule;
  }

  console.log("🛫 [SCHEDULE ADJUST] 항공편 시간에 맞춘 스케줄 조정 시작");
  console.log("✈️ [SCHEDULE] Selected Flight:", selectedFlight);

  const adjustedSchedule = JSON.parse(JSON.stringify(schedule)); // Deep copy

  // 첫날 스케줄 조정 (출국편 도착 시간 기준)
  adjustFirstDaySchedule(adjustedSchedule, selectedFlight);
  
  // 마지막날 스케줄 조정 (입국편 출발 시간 기준)
  adjustLastDaySchedule(adjustedSchedule, selectedFlight);

  console.log("✅ [SCHEDULE ADJUST] 스케줄 조정 완료");
  return adjustedSchedule;
};

/**
 * 첫날 스케줄 조정 (출국편 도착 시간 기준)
 */
const adjustFirstDaySchedule = (schedule, flight) => {
  const arrivalTime = flight.outbound_arrival_time;
  if (!arrivalTime || schedule.length === 0) return;

  const firstDay = schedule[0];
  if (!firstDay) return;

  try {
    const arrivalDate = new Date(arrivalTime);
    const arrivalHour = arrivalDate.getHours();
    
    console.log(`🛬 [FIRST DAY] 도착 시간: ${formatTime(arrivalTime)} (${arrivalHour}시)`);

    if (arrivalHour >= 18) {
      // 저녁 늦게 도착 → 호텔 체크인만
      console.log("🌙 [FIRST DAY] 늦은 도착 → 호텔 체크인만");
      firstDay.events = [
        {
          time_slot: "저녁",
          place_name: "호텔 체크인",
          description: `${formatTime(arrivalTime)} 도착 후 호텔 휴식 및 체크인`,
          icon: "home"
        }
      ];
    } else if (arrivalHour >= 15) {
      // 오후 늦게 도착 → 저녁 일정만
      console.log("🌅 [FIRST DAY] 오후 도착 → 저녁 일정만");
      firstDay.events = [
        {
          time_slot: "저녁",
          place_name: "호텔 체크인",
          description: `${formatTime(arrivalTime)} 도착 후 호텔 체크인`,
          icon: "home"
        },
        ...firstDay.events.filter(event => 
          event.time_slot && event.time_slot.includes('저녁')
        ).slice(0, 2) // 저녁 일정 최대 2개만
      ];
    } else if (arrivalHour >= 12) {
      // 오후 일찍 도착 → 오후/저녁 일정
      console.log("☀️ [FIRST DAY] 정오 도착 → 오후/저녁 일정");
      firstDay.events = [
        {
          time_slot: "오후",
          place_name: "호텔 체크인",
          description: `${formatTime(arrivalTime)} 도착 후 호텔 체크인 및 휴식`,
          icon: "home"
        },
        ...firstDay.events.filter(event => 
          event.time_slot && (event.time_slot.includes('오후') || event.time_slot.includes('저녁'))
        ).slice(0, 3)
      ];
    } else {
      // 오전 도착 → 점심부터 일정
      console.log("🌄 [FIRST DAY] 오전 도착 → 점심부터 일정");
      firstDay.events = [
        {
          time_slot: "점심",
          place_name: "호텔 체크인",
          description: `${formatTime(arrivalTime)} 도착 후 호텔 체크인`,
          icon: "home"
        },
        ...firstDay.events.filter(event => 
          event.time_slot && !event.time_slot.includes('오전')
        ).slice(0, 4)
      ];
    }

  } catch (error) {
    console.error("❌ [FIRST DAY] 첫날 스케줄 조정 오류:", error);
  }
};

/**
 * 마지막날 스케줄 조정 (입국편 출발 시간 기준)
 */
const adjustLastDaySchedule = (schedule, flight) => {
  const departureTime = flight.inbound_departure_time;
  if (!departureTime || schedule.length === 0) return;

  const lastDay = schedule[schedule.length - 1];
  if (!lastDay) return;

  try {
    const departureDate = new Date(departureTime);
    const departureHour = departureDate.getHours();
    
    console.log(`🛫 [LAST DAY] 출발 시간: ${formatTime(departureTime)} (${departureHour}시)`);

    if (departureHour <= 10) {
      // 오전 일찍 출발 → 호텔에서 공항 직행
      console.log("🌄 [LAST DAY] 이른 출발 → 공항 이동만");
      lastDay.events = [
        {
          time_slot: "오전",
          place_name: "호텔 체크아웃",
          description: "짐 정리 및 체크아웃",
          icon: "home"
        },
        {
          time_slot: "오전",
          place_name: "공항 이동",
          description: `${formatTime(departureTime)} 출발편 준비`,
          icon: "plane"
        }
      ];
    } else if (departureHour <= 14) {
      // 오후 일찍 출발 → 오전 일정 + 공항
      console.log("☀️ [LAST DAY] 정오 출발 → 오전 일정만");
      lastDay.events = [
        ...lastDay.events.filter(event => 
          event.time_slot && event.time_slot.includes('오전')
        ).slice(0, 2),
        {
          time_slot: "점심",
          place_name: "공항 이동",
          description: `${formatTime(departureTime)} 출발편 준비 (2시간 전 공항 도착)`,
          icon: "plane"
        }
      ];
    } else if (departureHour <= 17) {
      // 오후 늦게 출발 → 오전/점심 일정
      console.log("🌅 [LAST DAY] 오후 출발 → 오전/점심 일정");
      lastDay.events = [
        ...lastDay.events.filter(event => 
          event.time_slot && (event.time_slot.includes('오전') || event.time_slot.includes('점심'))
        ).slice(0, 3),
        {
          time_slot: "오후",
          place_name: "공항 이동",
          description: `${formatTime(departureTime)} 출발편 준비`,
          icon: "plane"
        }
      ];
    } else {
      // 저녁 출발 → 오후까지 일정
      console.log("🌙 [LAST DAY] 저녁 출발 → 오후까지 일정");
      lastDay.events = [
        ...lastDay.events.filter(event => 
          event.time_slot && !event.time_slot.includes('저녁')
        ).slice(0, 4),
        {
          time_slot: "저녁",
          place_name: "공항 이동",
          description: `${formatTime(departureTime)} 출발편 준비`,
          icon: "plane"
        }
      ];
    }

  } catch (error) {
    console.error("❌ [LAST DAY] 마지막날 스케줄 조정 오류:", error);
  }
};

export default adjustScheduleWithFlightTimes;