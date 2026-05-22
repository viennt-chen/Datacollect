<template>
  <v-app>
    <router-view />

    <!-- Global snackbar -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
      location="top"
    >
      {{ snackbar.message }}
      <template v-slot:actions>
        <v-btn variant="text" @click="snackbar.show = false">关闭</v-btn>
      </template>
    </v-snackbar>

    <!-- Global confirm dialog -->
    <v-dialog v-model="dialog.show" max-width="400" persistent>
      <v-card>
        <v-card-title class="d-flex align-center ga-2">
          <v-icon :icon="dialog.type === 'warning' ? 'mdi-alert' : 'mdi-information'" :color="dialog.type === 'warning' ? 'warning' : 'info'" />
          {{ dialog.title }}
        </v-card-title>
        <v-divider />
        <v-card-text>{{ dialog.message }}</v-card-text>
        <v-divider />
        <v-card-actions>
          <v-spacer />
          <v-btn variant="text" @click="handleConfirmCancel">取消</v-btn>
          <v-btn color="primary" @click="handleConfirmOk">确定</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-app>
</template>

<script setup>
import { snackbarState as snackbar, dialogState as dialog, handleConfirmOk, handleConfirmCancel } from '@/composables/useMessage'
</script>
