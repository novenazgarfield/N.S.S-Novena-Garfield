import { create } from 'zustand';
import { persist } from 'zustand/middleware';

// 桌宠状态管理
export const usePetStore = create(
  persist(
    (set, get) => ({
      // 桌宠基本信息
      petInfo: {
        name: '长离',
        level: 1,
        experience: 0,
        mood: 'happy', // 'happy' | 'sad' | 'excited' | 'tired' | 'focused'
        energy: 100,
        lastInteraction: Date.now()
      },

      // 当前状态
      currentAnimation: 'idle',
      currentActivity: null, // 'learning' | 'chatting' | 'listening' | 'practicing'
      isVisible: true,
      position: { x: 100, y: 100 },

      // 学习统计
      learningStats: {
        totalWordsLearned: 0,
        totalChatMessages: 0,
        totalMusicPlayed: 0,
        studyTimeToday: 0,
        streakDays: 0
      },

      // 设置
      settings: {
        autoHide: false,
        soundEnabled: true,
        animationSpeed: 'normal', // 'slow' | 'normal' | 'fast'
        theme: 'default'
      },

      // Actions
      updatePetInfo: (updates) => set((state) => ({
        petInfo: { ...state.petInfo, ...updates }
      })),

      setAnimation: (animation) => set({ currentAnimation: animation }),

      setActivity: (activity) => set({ currentActivity: activity }),

      updatePosition: (position) => set({ position }),

      toggleVisibility: () => set((state) => ({ isVisible: !state.isVisible })),

      updateLearningStats: (updates) => set((state) => ({
        learningStats: { ...state.learningStats, ...updates }
      })),

      updateSettings: (updates) => set((state) => ({
        settings: { ...state.settings, ...updates }
      })),

      // 增加经验值
      addExperience: (amount) => set((state) => {
        const newExperience = state.petInfo.experience + amount;
        const newLevel = Math.floor(newExperience / 100) + 1;
        
        return {
          petInfo: {
            ...state.petInfo,
            experience: newExperience,
            level: newLevel,
            lastInteraction: Date.now()
          }
        };
      }),

      // 更新心情
      updateMood: (mood) => set((state) => ({
        petInfo: { ...state.petInfo, mood, lastInteraction: Date.now() }
      })),

      // 更新能量
      updateEnergy: (energy) => set((state) => ({
        petInfo: { ...state.petInfo, energy: Math.max(0, Math.min(100, energy)) }
      })),

      // 记录互动
      recordInteraction: (type, data = {}) => {
        const state = get();
        const now = Date.now();
        
        set({
          petInfo: {
            ...state.petInfo,
            lastInteraction: now
          }
        });

        // 根据互动类型更新统计
        switch (type) {
          case 'word_learned':
            set((state) => ({
              learningStats: {
                ...state.learningStats,
                totalWordsLearned: state.learningStats.totalWordsLearned + 1
              }
            }));
            break;
          case 'chat_message':
            set((state) => ({
              learningStats: {
                ...state.learningStats,
                totalChatMessages: state.learningStats.totalChatMessages + 1
              }
            }));
            break;
          case 'music_played':
            set((state) => ({
              learningStats: {
                ...state.learningStats,
                totalMusicPlayed: state.learningStats.totalMusicPlayed + 1
              }
            }));
            break;
        }
      },

      // 重置桌宠状态
      resetPet: () => set({
        petInfo: {
          name: '长离',
          level: 1,
          experience: 0,
          mood: 'happy',
          energy: 100,
          lastInteraction: Date.now()
        },
        learningStats: {
          totalWordsLearned: 0,
          totalChatMessages: 0,
          totalMusicPlayed: 0,
          studyTimeToday: 0,
          streakDays: 0
        }
      })
    }),
    {
      name: 'pet-store',
      partialize: (state) => ({
        petInfo: state.petInfo,
        learningStats: state.learningStats,
        settings: state.settings,
        position: state.position
      })
    }
  )
);